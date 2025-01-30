# AutoReframer
Auto Reframes video from original to cropped size, following an object inside the video. Basically AI-Reframe.

If you edit videos, you may have found that a feature called Auto-Reframe exists that can be used to convert horizontal video to vertical without having black bars, by cropping the image. This is sometimes a paid software or doesn't follow the object/person the way you want it to.
I made this Auto-Reframer, using YOLO to detect and track objects. After detecting objects in the video, you can choose one object "id" and a crop size to Reframe any mp4 video of your choosing.
If you need any help running it you can just run: python3 track.py -h.

PS: My pc can't run Davinci Resolve's tracker very well.

# FUTURE IMPROVEMENTS
1. Add audio to the video.
2. Enable multiple priority object tracking. Eg: If i want to follow object with id=1 and in the middle of the video it leaves the video, I could choose to track object with id=2 until it leaves the video, and so on until the last frame.
3. Add a smoothness factor - If an object is too fast, the reframe might look "jiterry".
