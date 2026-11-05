#!/usr/bin/env bash
# refkit - turn performance footage into reference stills for 3D modelling.
#
# The useful output is stills, not video. A 90-minute set shows a conga rig
# clearly for maybe 40 seconds; scene-change detection finds those moments
# instead of making you scrub.
#
#   refkit.sh fetch    <url> [label]        download to reference/video/
#   refkit.sh frames   <video> [scene|N]    stills: scene changes, or every N sec
#   refkit.sh sheet    <frames-dir>         contact sheets for fast culling
#   refkit.sh pipeline <url> [label]        all three
#
# Scene threshold: 0.3 = more frames, 0.5 = fewer. Default 0.4.
set -euo pipefail

REF=/workspace/reference
THRESH="${SCENE_THRESHOLD:-0.4}"
MAXW="${MAX_WIDTH:-1600}"

die() { echo "error: $*" >&2; exit 1; }

cmd_fetch() {
  local url="${1:?usage: fetch <url> [label]}" label="${2:-}"
  mkdir -p "$REF/video"
  # Sleep between requests so a channel pull does not get throttled.
  yt-dlp \
    --sleep-requests 2 --retries 5 --no-overwrites \
    --format 'bestvideo[height<=1080]+bestaudio/best[height<=1080]' \
    --merge-output-format mp4 \
    --output "$REF/video/${label:+${label}__}%(uploader)s__%(title)s.%(ext)s" \
    --restrict-filenames \
    --write-info-json \
    "$url"
  echo "--> $REF/video"
}

cmd_frames() {
  local video="${1:?usage: frames <video> [scene|N]}" mode="${2:-scene}"
  [ -f "$video" ] || die "no such file: $video"
  local name out
  name=$(basename "$video"); name="${name%.*}"
  out="$REF/frames/$name"
  mkdir -p "$out"

  # Hardware decode when the build supports it; CPU otherwise.
  local hw=()
  if ffmpeg -hide_banner -decoders 2>/dev/null | grep -q nvdec; then
    hw=(-hwaccel cuda)
  fi

  local vf
  if [ "$mode" = "scene" ]; then
    vf="select='gt(scene,${THRESH})',scale=${MAXW}:-2"
    echo "scene-change extraction (threshold ${THRESH})"
  else
    vf="fps=1/${mode},scale=${MAXW}:-2"
    echo "interval extraction (every ${mode}s)"
  fi

  ffmpeg -nostdin -hide_banner -loglevel error "${hw[@]}" \
    -i "$video" -vf "$vf" -vsync vfr -q:v 2 \
    "$out/%04d.jpg"

  echo "$(find "$out" -name '*.jpg' | wc -l) frames --> $out"
}

cmd_sheet() {
  local dir="${1:?usage: sheet <frames-dir>}"
  [ -d "$dir" ] || die "no such dir: $dir"
  local name out
  name=$(basename "$dir")
  out="$REF/contact/$name"
  mkdir -p "$out"

  # 4x3 grid per sheet keeps each thumbnail big enough to judge gear.
  ffmpeg -nostdin -hide_banner -loglevel error \
    -pattern_type glob -i "$dir/*.jpg" \
    -vf "scale=400:-2,tile=4x3" -q:v 3 \
    "$out/sheet_%03d.jpg"

  echo "$(find "$out" -name 'sheet_*.jpg' | wc -l) sheets --> $out"
}

cmd_pipeline() {
  local url="${1:?usage: pipeline <url> [label]}" label="${2:-}"
  cmd_fetch "$url" "$label"
  local newest
  newest=$(find "$REF/video" -name '*.mp4' -newer "$REF" -print0 2>/dev/null \
    | xargs -0 ls -t 2>/dev/null | head -1) || true
  [ -n "${newest:-}" ] || newest=$(ls -t "$REF/video"/*.mp4 2>/dev/null | head -1)
  [ -n "${newest:-}" ] || die "no video found after fetch"
  echo "processing: $(basename "$newest")"
  cmd_frames "$newest" scene
  cmd_sheet "$REF/frames/$(basename "${newest%.*}")"
}

case "${1:-}" in
  fetch)    shift; cmd_fetch "$@" ;;
  frames)   shift; cmd_frames "$@" ;;
  sheet)    shift; cmd_sheet "$@" ;;
  pipeline) shift; cmd_pipeline "$@" ;;
  *) sed -n '2,16p' "$0" | sed 's/^# \{0,1\}//'; exit 1 ;;
esac
