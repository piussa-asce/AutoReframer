from ultralytics import YOLO
import cv2
import argparse
import ffmpeg
import torch
import os
import sys

class ObjectTracker():

    def __init__(self, in_video_path: str, out_video_path: str) -> None:
        self.model = YOLO('./yolo/yolo11n.pt')
        if torch.cuda.is_available():
            self.model.to('cuda')
        self.yaml_path = "./yolo/bytetrack.yaml"
        self.in_video_path = in_video_path
        self.out_video_path = out_video_path
        self.fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    def determine_x(self, center: int, crop_width: int, input_width: int) -> tuple:
        x_min = int(center - crop_width / 2)
        x_max = int(center + crop_width / 2)
        # cannot crop outside of image
        if x_min < 0: 
            x_min, x_max = 0, crop_width
        if x_max > input_width:
            x_max = input_width
            x_min = input_width - crop_width
        return (x_min, x_max)

    def track_all_objects(self) -> None:

        cap = cv2.VideoCapture(self.in_video_path)
        fps = round(cap.get(cv2.CAP_PROP_FPS))
        video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        output_video = cv2.VideoWriter(self.out_video_path, self.fourcc, fps, (video_width, video_height))

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Error retriveing frame while tracking all objects.")
                return
            results = self.model.track(source=frame, persist=True, tracker=self.yaml_path)
            # get all object's bounding boxes
            boxes = results[0].boxes.xyxy.cpu().numpy().astype(int)
            if results[0].boxes.id == None:
                return
            # get all object's tracking ids
            ids = results[0].boxes.id.cpu().numpy().astype(int)
            
            # draw boxes around all tracked objects
            for box, id in zip(boxes, ids):
                cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), (255, 0, 255), 5)
                cv2.putText(frame, f"Id {id}", (box[0], box[1]), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 255), 3)

            output_video.write(frame) # write frame to output video
            frame = cv2.resize(frame, (1280, 720))
            cv2.imshow('frame', frame)
            if cv2.waitKey(1) == ord('q'):
                break

        output_video.release()
        cap.release()
        cv2.destroyAllWindows()


    def track_object(self, track_id: int, crop_size: tuple) -> None:

        cap = cv2.VideoCapture(self.in_video_path)
        fps = round(cap.get(cv2.CAP_PROP_FPS))
        video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        out_width = crop_size[0] if crop_size[0] <= video_width else video_width # avoid cropping outside the image
        out_height = crop_size[1] if crop_size[1] <= video_height else video_height # avoid cropping outside the image

        output_video = cv2.VideoWriter(self.out_video_path, self.fourcc, fps, (out_width, out_height))

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Error retriveing frame while tracking all objects.")
                return

            results = self.model.track(source=frame, persist=True, tracker=self.yaml_path)
            boxes = results[0].boxes.xyxy.cpu().numpy().astype(int)
            if results[0].boxes.id == None:
                break
            ids = results[0].boxes.id.cpu().numpy().astype(int)

            for box, id in zip(boxes, ids):
                if track_id == id:
                    x_center = int(box[0] + (box[2] - box[0]) / 2)
                    x_min, x_max = self.determine_x(x_center, out_width, video_width)
                    
                    y_min = int((video_height / 2) - (out_height / 2))
                    y_max = int((video_height / 2) + (out_height / 2))

                    frame = frame[y_min:y_max, x_min:x_max] # crop frame
                    break
            
            output_video.write(frame)

        output_video.release()
        cap.release()
        cv2.destroyAllWindows()

def run_track_all_objects(input, output):
    ot = ObjectTracker(input, output)
    ot.track_all_objects()

def run_track_object(input, output, track_id, crop_size):
    ot = ObjectTracker(input, output)
    ot.track_object(track_id, crop_size)

def main():

    parser = argparse.ArgumentParser(
        prog="AutoReframe",
        description="Tracks multiple objects or Auto-Reframes a specific object"
    )

    parser.add_argument('input_video', type=str, help="Path to the mp4 input video file. (0, 1, ...) to use a camera instead.")
    parser.add_argument('track_id', type=int, const=None, nargs='?', help="Id to be tracked for the reframe. (Optional)")
    parser.add_argument('crop_width', type=int, const=1080, nargs='?', help="Number of pixels for the width of the reframed video. (Optional)")
    parser.add_argument('crop_height', type=int, const=1920, nargs='?', help="Number of pixels for the height of the reframed video. (Optional)")

    args = parser.parse_args()

    if not os.path.exists(args.input_video):
        print(f"Input file {args.input_video} does not exist.")
        sys.exit(0)

    if not os.path.exists("./out/"):
        os.mkdir("./out/")

    output_video = "./out/" + args.input_video.split("/")[-1][:-4] + "_out.MP4" # removes directories and the .mp4
    print(output_video)

    if args.track_id == None:
        print(f"Tracking all objects in video file {args.input_video}")
        run_track_all_objects(input=args.input_video, output=output_video)
    else:
        print(f"Tracking object with id {args.track_id} in video file {args.input_video}")
        run_track_object(input=args.input_video, output=output_video, track_id=args.track_id, 
                            crop_size=(args.crop_width, args.crop_height))

if __name__ == '__main__':
    main()