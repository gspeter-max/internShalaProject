import moviepy

video_file = moviepy.VideoFileClip('video.mp4')
audio_file = moviepy.AudioFileClip( 'music.mp3')

final_duration = min( video_file.duration, audio_file.duration)
final_audio = audio_file.subclipped( end_time = final_duration )
final_video = video_file.subclipped( end_time = final_duration )

final_video = final_video.with_audio(final_audio)
final_video.write_videofile('final_video.mp4')