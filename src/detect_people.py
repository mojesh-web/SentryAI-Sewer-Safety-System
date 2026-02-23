import os
import json
import cv2
from datetime import datetime
from ultralytics import YOLO
from config import VIDEO_PATH, OUTPUT_PATH, ZONE_POLYGON
from zone_utils import draw_zone, point_in_polygon

EVENTS_JSON_PATH = "outputs/events_log.json"
SNAPSHOT_DIR = "outputs/event_snapshots"


def iou_xyxy(a, b):
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b

    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    iw, ih = max(0, ix2 - ix1), max(0, iy2 - iy1)

    inter = iw * ih
    area_a = max(0, ax2 - ax1) * max(0, ay2 - ay1)
    area_b = max(0, bx2 - bx1) * max(0, by2 - by1)
    union = area_a + area_b - inter if (area_a + area_b - inter) > 0 else 1
    return inter / union


def main():
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)

    # Person detection model
    model = YOLO("yolov8n.pt")

    # Helmet detection model (downloaded to models folder)
    helmet_model = YOLO("models/helmet_best.pt")
    print("Helmet model classes:", helmet_model.names)

    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {VIDEO_PATH}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    out = cv2.VideoWriter(
        OUTPUT_PATH,
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (w, h)
    )

    events = []
    previous_inside = False
    frame_idx = 0

    # Cooldown to avoid duplicate entry triggers due to detection jitter
    cooldown_frames = int((fps or 25) * 2)  # 2 seconds
    last_event_frame = -10**9

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        results = model.predict(frame, conf=0.35, verbose=False)[0]

        # draw restricted zone
        draw_zone(frame, ZONE_POLYGON)

        current_inside = False
        persons = []

        # collect person boxes + whether inside
        for box in results.boxes:
            cls = int(box.cls[0].item())
            name = model.names.get(cls, str(cls))
            if name != "person":
                continue

            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

            inside = point_in_polygon((cx, cy), ZONE_POLYGON)
            if inside:
                current_inside = True

            persons.append((x1, y1, x2, y2, inside))

            color = (0, 0, 255) if inside else (0, 255, 0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

        # Trigger only when crossing OUT -> IN, and not within cooldown window
        if current_inside and (not previous_inside) and (frame_idx - last_event_frame) > cooldown_frames:

            # Helmet detection on this frame only
            helmet_results = helmet_model.predict(frame, conf=0.30, verbose=False)[0]

            helmet_boxes = []
            for hb in helmet_results.boxes:
                hcls = int(hb.cls[0].item())
                hname = helmet_model.names.get(hcls, str(hcls)).lower()
                # Only accept the positive class: Hardhat
            helmet_boxes = []
            for hb in helmet_results.boxes:
                hcls = int(hb.cls[0].item())
                hname = helmet_model.names.get(hcls, str(hcls)).lower()

                # Only accept the positive class: Hardhat
                if hname == "hardhat":
                    hx1, hy1, hx2, hy2 = map(int, hb.xyxy[0].tolist())
                    helmet_boxes.append((hx1, hy1, hx2, hy2))

            # Determine helmet presence for any person inside zone
            helmet_present = False
            for (px1, py1, px2, py2, pinside) in persons:
                if not pinside:
                    continue

                # head region: top 35% of person box
                head_box = (px1, py1, px2, py1 + int(0.35 * (py2 - py1)))

                for hb in helmet_boxes:
                    if iou_xyxy(head_box, hb) > 0.05:
                        helmet_present = True
                        break

                if helmet_present:
                    break

            risk_level = "LOW" if helmet_present else "HIGH"

            ts = datetime.now().isoformat(timespec="seconds")
            snapshot_path = os.path.join(
                SNAPSHOT_DIR,
                f"entry_{frame_idx}_{ts.replace(':','-')}.jpg"
            )

            cv2.imwrite(snapshot_path, frame)

            event = {
                "timestamp": ts,
                "event": "entry_detected",
                "frame_index": frame_idx,
                "snapshot_path": snapshot_path,
                "ppe": {"helmet": helmet_present},
                "risk_level": risk_level
            }

            events.append(event)
            last_event_frame = frame_idx  # cooldown anchor

            msg = f"EVENT: {risk_level} RISK ENTRY"
            cv2.putText(frame, msg, (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)

            print("Entry event triggered:", event)

        previous_inside = current_inside
        out.write(frame)
        frame_idx += 1

    cap.release()
    out.release()

    with open(EVENTS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=4)

    print("Saved output video:", OUTPUT_PATH)
    print("Saved events log:", EVENTS_JSON_PATH)
    print("Snapshots saved in:", SNAPSHOT_DIR)


if __name__ == "__main__":
    main()
