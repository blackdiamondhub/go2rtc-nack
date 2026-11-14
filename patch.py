"""Make go2rtc's WebRTC sender answer NACKs.

go2rtc registers pion's default interceptors (NACK responder, etc.) but never
reads RTCP from its RTPSenders, so the interceptors never see the browser's
NACK/PLI feedback and lost UDP packets are never retransmitted. This starts a
reader goroutine for every sender track.

Run from the root of a go2rtc checkout. Exits non-zero if the code it hooks
into has changed, so a new upstream release can't silently ship unpatched.
"""
import pathlib
import sys

CONSUMER = pathlib.Path("pkg/webrtc/consumer.go")
CONN = pathlib.Path("pkg/webrtc/conn.go")

ANCHOR = (
    "\tlocalTrack := c.GetSenderTrack(media.ID)\n"
    "\tif localTrack == nil {\n"
    "\t\treturn errors.New(\"webrtc: can't get track\")\n"
    "\t}\n"
)

READER = '''
// readSenderRTCP drains RTCP from the RTPSender so pion interceptors
// (NACK responder, etc.) actually process feedback from the remote peer.
func (c *Conn) readSenderRTCP(mid string) {
	tr := c.getTranseiver(mid)
	if tr == nil || tr.Sender() == nil {
		return
	}
	go func(s *webrtc.RTPSender) {
		buf := make([]byte, 1500)
		for {
			if _, _, err := s.Read(buf); err != nil {
				return
			}
		}
	}(tr.Sender())
}
'''


def main() -> int:
    consumer = CONSUMER.read_bytes().decode()
    conn = CONN.read_bytes().decode()
    if "readSenderRTCP" in consumer or "readSenderRTCP" in conn:
        print("already patched")
        return 0
    if consumer.count(ANCHOR) != 1:
        print(f"anchor not found exactly once in {CONSUMER}", file=sys.stderr)
        return 1
    if "func (c *Conn) getTranseiver(" not in conn:
        print(f"getTranseiver not found in {CONN}", file=sys.stderr)
        return 1
    CONSUMER.write_bytes(consumer.replace(ANCHOR, ANCHOR + "\n\tc.readSenderRTCP(media.ID)\n").encode())
    CONN.write_bytes((conn + READER).encode())
    print("patched")
    return 0


if __name__ == "__main__":
    sys.exit(main())
