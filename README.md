# go2rtc-nack

[go2rtc](https://github.com/AlexxIT/go2rtc) with three WebRTC fixes taken from
open upstream pull requests, pinned as patch files in `patches/`:

| Patch | Upstream PR | What it does |
|---|---|---|
| `0001` | [#2486](https://github.com/AlexxIT/go2rtc/pull/2486) | Reads RTCP from each `RTPSender` so pion's NACK responder sees the browser's NACKs and retransmits lost packets, instead of the video freezing until the next keyframe. |
| `0002`, `0003` | [#2684](https://github.com/AlexxIT/go2rtc/pull/2684) | Caps NACK resends per stream (bytes per 500 ms window tied to the stream's own rate, at most 5 per packet). Without it one peer can make go2rtc resend ~1000x its NACK traffic. |
| `0004` | [#2685](https://github.com/AlexxIT/go2rtc/pull/2685) | Forwards a viewer's PLI/FIR to the source. For RTSP sources that ignore PLI (UniFi Protect), the opt-in `#keyframe=resetup` URL option gets a fresh keyframe via a short RTSP SETUP/TEARDOWN, at most once per second per source. Off unless a stream URL opts in. |

Measured on the BlackDiamondHub cameras page with the NACK fix: stock go2rtc
had 3-6% loss and freezes on UDP with zero retransmits; the patched build had
essentially none.

## Image

```
ghcr.io/blackdiamondlodge/go2rtc-nack:latest
```

A drop-in replacement for `alexxit/go2rtc` (built with upstream's own
`docker/Dockerfile`, amd64 + arm64).

Tags:
- `latest`: newest upstream release, patched
- `vX.Y.Z`: that upstream release, patched
- `vX.Y.Z-nack-<sha>`: that release with this repo's patches at `<sha>`

## How it stays current

`.github/workflows/build.yml` runs daily. When upstream publishes a new release
it clones that tag, runs `apply-patches.sh`, builds, runs the tests of the
patched packages, smoke-tests and pushes. A patch that no longer applies fails
the build rather than shipping an unpatched image. A patch upstream has already
merged is detected and skipped; delete it from `patches/` when convenient.

To refresh a patch from an updated upstream PR, export its commits with
`git format-patch` and replace the file.

Run it by hand from Actions, optionally with a specific upstream tag or
`force` to rebuild.