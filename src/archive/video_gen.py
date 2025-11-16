@app.get("/reddit")
async def get_stories():
    #http://localhost:8000/redditcallback
    reddit = praw.Reddit(
        client_id="E2uNJXLYl00rmHZU3VxNiA",
        client_secret="93sg0Hcar5KOE0Luwb_swi7V2L8MkA",
        user_agent="script:tktok:1.0 (by /u/branana-bread)"
    )
    #AITAH, talesfromtechsupport, TalesFromRetail, Best of RedditorUpdates, Off my chest
    subreddit = reddit.subreddit("AITAH")
    posts = subreddit.hot(limit=3)
    seen_posts = set()
    unique_stories = []
    for post in posts:
        if post.id not in seen_posts:
            seen_posts.add(post.id)
            story = {
                "title": post.title,
                "url": post.url,
                "score": post.score,
                "author": str(post.author),
                "permalink": f"https://reddit.com{post.permalink}",
                "selftext": post.selftext.replace("\n", "").replace('"', "").replace(" and", " ,and")
            }
            unique_stories.append(story)
    
    story = unique_stories[2]
    file = generate_tts_audio(story["selftext"])
    file = speed_up_audio(file)
    language, words = transcribe(file)
    subtitle_file = generate_subtitle_file(
        language=language,
        words=words
    )
    add_subtitle_to_video(
        soft_subtitle=True,
        subtitle_file=subtitle_file,
        subtitle_language=language
    )
    return unique_stories

def speed_up_audio(audio, speed=1.3):
    sound = AudioSegment.from_file(audio)
    spd = sound.speedup(speed, 150, 25)
    spd.export(audio, format = 'mp3')
    return audio

def generate_tts_audio(text, lang="en", output_file="output/tts_audio.mp3"):
    """Generate TTS audio from text."""
    tts = gTTS(text=text, lang=lang)
    tts.save(output_file)
    return output_file

def transcribe(audio):
    model = WhisperModel("small")
    segments, info = model.transcribe(audio, word_timestamps=True)
    language = info.language
    print("Transcription language", info.language)
    segments = list(segments)
    words = []
    for segment in segments:
        for word in segment.words:
            words.append(word)
            # print("[%.2fs -> %.2fs] %s" % (word.start, word.end, word.word))
    return language, words

def format_time(seconds):
    hours = math.floor(seconds / 3600)
    seconds %= 3600
    minutes = math.floor(seconds / 60)
    seconds %= 60
    milliseconds = round((seconds - math.floor(seconds)) * 1000)
    seconds = math.floor(seconds)
    formatted_time = f"{hours:02d}:{minutes:02d}:{seconds:01d},{milliseconds:03d}"

    return formatted_time

def generate_subtitle_file(language, words):
    subtitle_file = f"subtitles_temp.{language}.srt"
    text = ""
    for index, segment in enumerate(words):
        segment_start = format_time(segment.start)
        segment_end = format_time(segment.end)
        text += f"{str(index+1)} \n"
        text += f"{segment_start} --> {segment_end} \n"
        text += f"{segment.word} \n"
        text += "\n"
    f = open(subtitle_file, "w")
    f.write(text)
    f.close()
    return subtitle_file

def add_subtitle_to_video(soft_subtitle, subtitle_file,  subtitle_language):