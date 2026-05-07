from resemblyzer import VoiceEncoder, preprocess_wav
import librosa
import io  # Input/Output module (for streams) It deals with reading and writing data — especially in memory or through streams.
import numpy as np 
import streamlit as st


@st.cache_resource 
def load_voice_encoder():   # these is Because we don't want to Re run again this VoiceEncoder function again again as its heavy 
    return VoiceEncoder()

def get_voice_embeddings(audio_bytes):
    try:
        audio, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)  
        # io.BytesIO -> storing audio bytes in file like structure in memory to read by librosa 
        # sr = sampling rate 16000 Hz

        clean_audio = preprocess_wav(audio)

        encoder = load_voice_encoder()
        embeddings = encoder.embed_utterance(clean_audio)

        return embeddings.tolist()
    except Exception as e:
        st.error('Voice recogisation error')
        return None
    

def identify_speaker(new_embedding, stored_embeddings_dict, thresold=0.65):

    if new_embedding is None or not stored_embeddings_dict:
        return None, 0.0

    best_st_id = None
    best_score = -1

    for st_id, embedding in stored_embeddings_dict.items():
        if embedding:
            similarity = np.dot(new_embedding, embedding)
            if similarity > best_score: 
                best_score = similarity
                best_st_id = st_id
    
    if best_score >= thresold :
        return best_st_id, best_score
    
    return None, best_score


def process_bulk_audio(audio_bytes, candidates_dict, thresold=0.65):
    try:
        audio, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)

        # Split audio into non-silent segments
        # Example output: [(0, 8000), (10000, 20000)]
        segments = librosa.effects.split(audio, top_db=30)

        # Dictionary to store final results
        # Example: {"Faiz": 0.87}
        identified_results = {}

        # Loop through each segment (start index, end index)
        for start, end in segments:

            # Skip very short segments (< 0.5 sec)
            if (end - start) < sr * 0.5:
                continue 

            # Extract part of audio
            # Example: audio[0:8000]
            segment_audio = audio[start:end]

            # Clean audio (normalize, remove noise, etc.)
            cleaned_audio = preprocess_wav(segment_audio)

            # Load voice encoder model
            encoder = load_voice_encoder()

            # Convert audio → embedding (vector)
            # Example: [0.12, 0.98, 0.45, ...]
            embedding = encoder.embed_utterance(cleaned_audio)

            # Identify speaker using similarity
            # Example output: ("Faiz", 0.82)
            st_id, score = identify_speaker(embedding, candidates_dict, thresold)

            # If a speaker is detected
            if st_id:

                # Store only best score for each speaker
                if st_id not in identified_results or score > identified_results[st_id]:
                    identified_results[st_id] = score

        return identified_results

    except Exception as e:
        st.error('Bulk process error')
        return {}
                

    
        