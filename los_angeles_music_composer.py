# -*- coding: utf-8 -*-
"""Los_Angeles_Music_Composer.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1XEn1oa_3Y-OI07ztLQpNsdZATebUMRs-

# Los Angeles Music Composer (ver. 2.0)

***

Powered by tegridy-tools: https://github.com/asigalov61/tegridy-tools

***

WARNING: This complete implementation is a functioning model of the Artificial Intelligence. Please excercise great humility, care, and respect. https://www.nscai.gov/

***

#### Project Los Angeles

#### Tegridy Code 2023

***

# (GPU CHECK)
"""

#@title NVIDIA GPU check
!nvidia-smi

"""# (SETUP ENVIRONMENT)"""

#@title Install dependencies
!git clone https://github.com/asigalov61/Los-Angeles-Music-Composer
!pip install torch
!pip install einops
!pip install torch-summary
!pip install sklearn
!pip install tqdm
!pip install matplotlib
!apt install fluidsynth #Pip does not work for some reason. Only apt works
!pip install midi2audio

# Commented out IPython magic to ensure Python compatibility.
#@title Import modules

print('=' * 70)
print('Loading core Los Angeles Music Composer modules...')

import os
import pickle
import random
import secrets
import statistics
from time import time
import tqdm

print('=' * 70)
print('Loading main Los Angeles Music Composer modules...')
import torch

# %cd /content/Los-Angeles-Music-Composer

import TMIDIX
from lwa_transformer import *

# %cd /content/
print('=' * 70)
print('Loading aux Los Angeles Music Composer modeules...')

import matplotlib.pyplot as plt

from torchsummary import summary
from sklearn import metrics

from midi2audio import FluidSynth
from IPython.display import Audio, display

print('=' * 70)
print('Done!')
print('Enjoy! :)')
print('=' * 70)

"""# (LOAD MODEL)"""

# Commented out IPython magic to ensure Python compatibility.
#@title Unzip Pre-Trained Los Angeles Music Composer Model
print('=' * 70)
# %cd /content/Los-Angeles-Music-Composer/Model

print('=' * 70)
print('Unzipping pre-trained Los Angeles Music Composer model...Please wait...')

!cat /content/Los-Angeles-Music-Composer/Model/Los_Angeles_Music_Composer_Trained_Model.zip* > /content/Los-Angeles-Music-Composer/Model/Los_Angeles_Music_Composer_Trained_Model.zip
print('=' * 70)

!unzip -j /content/Los-Angeles-Music-Composer/Model/Los_Angeles_Music_Composer_Trained_Model.zip
print('=' * 70)

print('Done! Enjoy! :)')
print('=' * 70)
# %cd /content/
print('=' * 70)

#@title Load Los Angeles Music Composer Model
full_path_to_model_checkpoint = "/content/Los-Angeles-Music-Composer/Model/Los_Angeles_Music_Composer_Model_88835_steps_0.643_loss.pth" #@param {type:"string"}

print('=' * 70)
print('Loading Los Angeles Music Composer Pre-Trained Model...')
print('Please wait...')
print('=' * 70)
print('Instantiating model...')

SEQ_LEN = 4096

# instantiate the model

model = LocalTransformer(
    num_tokens = 2831,
    dim = 1024,
    depth = 36,
    causal = True,
    local_attn_window_size = 512,
    max_seq_len = SEQ_LEN
)

model = torch.nn.DataParallel(model)

model.cuda()
print('=' * 70)

print('Loading model checkpoint...')

model.load_state_dict(torch.load(full_path_to_model_checkpoint))
print('=' * 70)

model.eval()

print('Done!')
print('=' * 70)

# Model stats
print('Model summary...')
summary(model)

# Plot Token Embeddings
tok_emb = model.module.token_emb.weight.detach().cpu().tolist()

tok_emb1 = []

for t in tok_emb:
    tok_emb1.append([abs(statistics.median(t))])

cos_sim = metrics.pairwise_distances(
   tok_emb1, metric='euclidean'
)
plt.figure(figsize=(7, 7))
plt.imshow(cos_sim, cmap="inferno", interpolation="nearest")
im_ratio = cos_sim.shape[0] / cos_sim.shape[1]
plt.colorbar(fraction=0.046 * im_ratio, pad=0.04)
plt.xlabel("Position")
plt.ylabel("Position")
plt.tight_layout()
plt.plot()
plt.savefig("/content/Los-Angeles-Music-Composer-Tokens-Embeddings-Plot.png", bbox_inches="tight")

"""# (LOAD SEED MIDI)"""

#@title Load Seed MIDI
select_seed_MIDI = "Los-Angeles-Music-Composer-Piano-Seed-1" #@param ["Los-Angeles-Music-Composer-Piano-Seed-1", "Los-Angeles-Music-Composer-Piano-Seed-2", "Los-Angeles-Music-Composer-Piano-Seed-3", "Los-Angeles-Music-Composer-Piano-Seed-4", "Los-Angeles-Music-Composer-Piano-Seed-5", "Los-Angeles-Music-Composer-MI-Seed-1", "Los-Angeles-Music-Composer-MI-Seed-2", "Los-Angeles-Music-Composer-MI-Seed-3", "Los-Angeles-Music-Composer-MI-Seed-4", "Los-Angeles-Music-Composer-MI-Seed-5"]
full_path_to_custom_seed_MIDI = "" #@param {type:"string"}

if full_path_to_custom_seed_MIDI == '':
  f = '/content/Los-Angeles-Music-Composer/Seeds/'+select_seed_MIDI+'.mid'

else:
  f = full_path_to_custom_seed_MIDI

print('=' * 70)
print('Los Angeles Music Composer Seed MIDI Loader')
print('=' * 70)
print('Loading seed MIDI...')
print('=' * 70)
print('File:', f)
print('=' * 70)

transpose_to_model_average_pitch = False

#=======================================================
# START PROCESSING

# Convering MIDI to ms score with MIDI.py module
score = TMIDIX.midi2ms_score(open(f, 'rb').read())

# INSTRUMENTS CONVERSION CYCLE
events_matrix = []
melody_chords_f = []
melody_chords_f1 = []
itrack = 1
patches = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

patch_map = [
            [0, 1, 2, 3, 4, 5, 6, 7], # Piano 
            [24, 25, 26, 27, 28, 29, 30], # Guitar
            [32, 33, 34, 35, 36, 37, 38, 39], # Bass
            [40, 41], # Violin
            [42, 43], # Cello
            [46], # Harp
            [56, 57, 58, 59, 60], # Trumpet
            [64, 65, 66, 67, 68, 69, 70, 71], # Sax
            [72, 73, 74, 75, 76, 77, 78], # Flute
            [-1], # Drums
            [52, 53], # Choir
            [16, 17, 18, 19, 20] # Organ
            ]

while itrack < len(score):
  for event in score[itrack]:         
      if event[0] == 'note' or event[0] == 'patch_change':
          events_matrix.append(event)
  itrack += 1

events_matrix.sort(key=lambda x: x[1])

events_matrix1 = []

for event in events_matrix:
  if event[0] == 'patch_change':
      patches[event[2]] = event[3]

  if event[0] == 'note':
      event.extend([patches[event[3]]])
      once = False

      for p in patch_map:
          if event[6] in p and event[3] != 9: # Except the drums
              event[3] = patch_map.index(p)
              once = True

      if not once and event[3] != 9: # Except the drums
          event[3] = 15 # All other instruments/patches channel
          event[5] = max(80, event[5])

      if event[3] < 12: # We won't write chans 12-16 for now...
          events_matrix1.append(event)
          # stats[event[3]] += 1

#=======================================================
# PRE-PROCESSING

# checking number of instruments in a composition
instruments_list_without_drums = list(set([y[3] for y in events_matrix1 if y[3] != 9]))

if len(events_matrix1) > 0 and len(instruments_list_without_drums) > 0:

  # recalculating timings
  for e in events_matrix1:
      e[1] = int(round(e[1] / 10)) # Max 1 seconds for start-times
      e[2] = int(round(e[2] / 20)) # Max 2 seconds for durations

  # Sorting by pitch, then by start-time
  events_matrix1.sort(key=lambda x: x[4], reverse=True)
  events_matrix1.sort(key=lambda x: x[1])

  #=======================================================
  # FINAL PRE-PROCESSING

  melody_chords = []

  pe = events_matrix1[0]

  for e in events_matrix1:
    if e[1] >= 0 and e[2] > 0:

      # Cliping all values...
      tim = max(0, min(127, e[1]-pe[1]))             
      dur = max(1, min(127, e[2]))
      cha = max(0, min(11, e[3]))
      ptc = max(1, min(127, e[4]))
      vel = max(8, min(127, e[5]))

      velocity = round(vel / 15)

      # Writing final note 
      melody_chords.append([tim, dur, cha, ptc, velocity])

      pe = e

  if len([y for y in melody_chords if y[2] != 9]) > 12: # Filtering out tiny/bad MIDIs...

    times = [y[0] for y in melody_chords[12:]]
    avg_time = sum(times) / len(times)

    times_list = list(set(times))

    instruments_list = list(set([y[2] for y in melody_chords]))
    num_instr = len(instruments_list)

    if avg_time < 112 and instruments_list != [9]: # Filtering out bad MIDIs...
      if 0 in times_list: # Filtering out (mono) melodies MIDIs

          #=======================================================
          # FINAL PROCESSING
          #=======================================================

          # Break between compositions / Intro seq

          if 9 in instruments_list:
            drums_present = 2818 # Yes
          else:
            drums_present = 2817 # No

          melody_chords_f.extend([2816, drums_present, 2819+(num_instr-1)])

          #=======================================================

          # Composition control seq
          intro_mode_time = statistics.mode([0] + [y[0] for y in melody_chords if y[2] != 9 and y[0] != 0])
          intro_mode_dur = statistics.mode([y[1] for y in melody_chords if y[2] != 9])
          intro_mode_pitch = statistics.mode([y[3] for y in melody_chords if y[2] != 9])
          intro_mode_velocity = statistics.mode([y[4] for y in melody_chords if y[2] != 9])

          # Instrument value 12 is reserved for composition control seq
          intro_dur_vel = (intro_mode_dur * 8) + (intro_mode_velocity-1)
          intro_cha_ptc = (12 * 128) + intro_mode_pitch

          melody_chords_f.extend([intro_mode_time, intro_dur_vel+128, intro_cha_ptc+1152])

          # TOTAL DICTIONARY SIZE 2831

          #=======================================================
          # MAIN PROCESSING CYCLE
          #=======================================================

          for m in melody_chords:

            # WRITING EACH NOTE HERE
            dur_vel = (m[1] * 8) + (m[4]-1)
            cha_ptc = (m[2] * 128) + m[3]

            melody_chords_f.extend([m[0], dur_vel+128, cha_ptc+1152])
            melody_chords_f1.append([m[0], dur_vel+128, cha_ptc+1152])

    #=======================================================
  
    song = melody_chords_f
    song_f = []
    tim = 0
    dur = 0
    vel = 0
    pitch = 0
    channel = 0

    son = []
    song1 = []

    for s in song:
      if s >= 128 and s < (12*128)+1152:
        son.append(s)
      else:
        if len(son) == 3:
          song1.append(son)
        son = []
        son.append(s)
                    
    for ss in song1:

      tim += ss[0] * 10

      dur = ((ss[1]-128) // 8) * 20
      vel = (((ss[1]-128) % 8)+1) * 15
   
      channel = (ss[2]-1152) // 128
      pitch = (ss[2]-1152) % 128
                      
      song_f.append(['note', tim, dur, channel, pitch, vel ])

    detailed_stats = TMIDIX.Tegridy_SONG_to_MIDI_Converter(song_f,
                                                          output_signature = 'Los Angeles Music Composer',  
                                                          output_file_name = '/content/Los-Angeles-Music-Composer-Seed-Composition',
                                                          track_name='Project Los Angeles',
                                                          list_of_MIDI_patches=[0, 24, 32, 40, 42, 46, 56, 71, 73, 0, 53, 19, 0, 0, 0, 0],
                                                          number_of_ticks_per_quarter=500)
        
    #=======================================================

print('=' * 70)
print('Composition stats:')
print('Composition has', len(melody_chords_f1), 'notes')
print('Composition has', len(melody_chords_f), 'tokens')
print('=' * 70)

print('Displaying resulting composition...')
print('=' * 70)

fname = '/content/Los-Angeles-Music-Composer-Seed-Composition'

x = []
y =[]
c = []

colors = ['red', 'yellow', 'green', 'cyan', 'blue', 'pink', 'orange', 'purple', 'gray', 'white', 'gold', 'silver']

for s in song_f:
  x.append(s[1] / 1000)
  y.append(s[4])
  c.append(colors[s[3]])

FluidSynth("/usr/share/sounds/sf2/FluidR3_GM.sf2", 16000).midi_to_audio(str(fname + '.mid'), str(fname + '.wav'))
display(Audio(str(fname + '.wav'), rate=16000))

plt.figure(figsize=(14,5))
ax=plt.axes(title=fname)
ax.set_facecolor('black')

plt.scatter(x,y, c=c)
plt.xlabel("Time")
plt.ylabel("Pitch")
plt.show()

"""# (GENERATE)"""

#@title Improv Generation

number_of_tokens_tp_generate = 1024 #@param {type:"slider", min:32, max:4064, step:32}
number_of_batches_to_generate = 4 #@param {type:"slider", min:1, max:16, step:1}

#@markdown Use custom MIDI sequences if you want to have model try to mimic custom MIDI composition. Or you can specify your own, completely custom sequence for the model to use

start_improv_sequence_type = "user_defined_seq" #@param ["custom_MIDI_instruments_seq", "custom_MIDI_instruments_and_composition_seq", "user_defined_seq"]

#@markdown Specify user-defined improv sequence below

drums_present_or_not = True #@param {type:"boolean"}
number_of_instruments = 4 #@param {type:"slider", min:1, max:12, step:1}

#@markdown NOTE: If you want to specify composition seq, you must specify all four parameters. All four parameters must be > 0

desired_time = 0 #@param {type:"slider", min:0, max:127, step:1}
desired_duration = 0 #@param {type:"slider", min:0, max:127, step:1}
desired_pitch = 0 #@param {type:"slider", min:0, max:127, step:1}
desired_velocity = 0 #@param {type:"slider", min:0, max:8, step:1}

#@markdown Other settings

allow_model_to_stop_generation_if_needed = False #@param {type:"boolean"}
temperature = 1 #@param {type:"slider", min:0.1, max:1, step:0.1}

print('=' * 70)
print('Los Angeles Music Composer Improv Model Generator')
print('=' * 70)

if allow_model_to_stop_generation_if_needed:
  min_stop_token = 2816
else:
  min_stop_token = 0

if start_improv_sequence_type == 'custom_MIDI_instruments_seq':
  outy = melody_chords_f[:3]

if start_improv_sequence_type == 'custom_MIDI_instruments_and_composition_seq':
  outy = melody_chords_f[:6]

if start_improv_sequence_type == 'user_defined_seq':
  if drums_present_or_not:
    drumsp = 1
  else:
    drumsp = 0

  outy = [2816, 2817+drumsp, 2819+((number_of_instruments)-1)]
  test_info = [desired_time, desired_duration, desired_pitch, desired_velocity]

  if 0 not in test_info:
    dur_vel = (desired_duration * 8) + (desired_velocity-1)
    cha_ptc = (12 * 128) + desired_pitch
    
    outy.extend([desired_time, dur_vel+128, cha_ptc+1152])

print('Selected Improv sequence:')
print(outy)
print('=' * 70)

inp = [outy] * number_of_batches_to_generate

inp = torch.LongTensor(inp).cuda()

#start_time = time()

out = model.module.generate(inp, 
                      number_of_tokens_tp_generate, 
                      temperature=temperature, 
                      return_prime=True, 
                      min_stop_token=min_stop_token, 
                      verbose=True)

out0 = out.tolist()

print('=' * 70)
print('Done!')
print('=' * 70)
#print('Generation took', time() - start_time, "seconds")
print('=' * 70)

#======================================================================

print('Rendering results...')
print('=' * 70)

for i in range(number_of_batches_to_generate):

  print('=' * 70)
  print('Batch #', i)
  print('=' * 70)

  out1 = out0[i]

  print('Sample INTs', out1[:12])
  print('=' * 70)

  if len(out) != 0:
    
      song = out1
      song_f = []
      tim = 0
      dur = 0
      vel = 0
      pitch = 0
      channel = 0

      son = []
      song1 = []

      for s in song:
        if s >= 128 and s < (12*128)+1152:
          son.append(s)
        else:
          if len(son) == 3:
            song1.append(son)
          son = []
          son.append(s)
                      
      for ss in song1:

        tim += ss[0] * 10

        dur = (((ss[1]-128) // 8)+1) * 20
        vel = (((ss[1]-128) % 8)+1) * 15
    
        channel = (ss[2]-1152) // 128
        pitch = (ss[2]-1152) % 128
                        
        song_f.append(['note', tim, dur, channel, pitch, vel ])

      detailed_stats = TMIDIX.Tegridy_SONG_to_MIDI_Converter(song_f,
                                                          output_signature = 'Los Angeles Music Composer',  
                                                          output_file_name = '/content/Los-Angeles-Music-Composer-Music-Composition_'+str(i), 
                                                          track_name='Project Los Angeles',
                                                          list_of_MIDI_patches=[0, 24, 32, 40, 42, 46, 56, 71, 73, 0, 53, 19, 0, 0, 0, 0],
                                                          number_of_ticks_per_quarter=500)


      print('=' * 70)
      print('Displaying resulting composition...')
      print('=' * 70)

      fname = '/content/Los-Angeles-Music-Composer-Music-Composition_'+str(i)

      x = []
      y =[]
      c = []

      colors = ['red', 'yellow', 'green', 'cyan', 'blue', 'pink', 'orange', 'purple', 'gray', 'white', 'gold', 'silver']

      for s in song_f:
        x.append(s[1] / 1000)
        y.append(s[4])
        c.append(colors[s[3]])

      FluidSynth("/usr/share/sounds/sf2/FluidR3_GM.sf2", 16000).midi_to_audio(str(fname + '.mid'), str(fname + '.wav'))
      display(Audio(str(fname + '.wav'), rate=16000))

      plt.figure(figsize=(14,5))
      ax=plt.axes(title=fname)
      ax.set_facecolor('black')

      plt.scatter(x,y, c=c)
      plt.xlabel("Time")
      plt.ylabel("Pitch")
      plt.show()

#@title Standard/Simple Continuation

number_of_prime_tokens = 512 #@param {type:"slider", min:4, max:3072, step:4}
number_of_tokens_to_generate = 1024 #@param {type:"slider", min:32, max:4096, step:32}
number_of_batches_to_generate = 4 #@param {type:"slider", min:1, max:16, step:1}
include_prime_tokens_in_generated_output = True #@param {type:"boolean"}
allow_model_to_stop_generation_if_needed = False #@param {type:"boolean"}
temperature = 1 #@param {type:"slider", min:0.1, max:1, step:0.1}

print('=' * 70)
print('Los Angeles Music Composer Standard Model Generator')
print('=' * 70)

if allow_model_to_stop_generation_if_needed:
  min_stop_token = 2816
else:
  min_stop_token = 0

outy = melody_chords_f[:number_of_prime_tokens]

inp = [outy] * number_of_batches_to_generate

inp = torch.LongTensor(inp).cuda()

#start_time = time()

out = model.module.generate(inp, 
                      number_of_tokens_to_generate, 
                      temperature=temperature, 
                      return_prime=include_prime_tokens_in_generated_output, 
                      min_stop_token=min_stop_token, 
                      verbose=True)

out0 = out.tolist()
print('=' * 70)
print('Done!')
print('=' * 70)
#print('Generation took', time() - start_time, "seconds")
#print('=' * 70)
#======================================================================
print('Rendering results...')
print('=' * 70)

for i in range(number_of_batches_to_generate):

  print('=' * 70)
  print('Batch #', i)
  print('=' * 70)

  out1 = out0[i]

  print('Sample INTs', out1[:12])
  print('=' * 70)

  if len(out) != 0:
      
      song = out1
      song_f = []
      tim = 0
      dur = 0
      vel = 0
      pitch = 0
      channel = 0

      son = []
      song1 = []

      for s in song:
        if s >= 128 and s < (12*128)+1152:
          son.append(s)
        else:
          if len(son) == 3:
            song1.append(son)
          son = []
          son.append(s)
                      
      for ss in song1:

        tim += ss[0] * 10

        dur = ((ss[1]-128) // 8) * 20
        vel = (((ss[1]-128) % 8)+1) * 15
    
        channel = (ss[2]-1152) // 128
        pitch = (ss[2]-1152) % 128
                        
        song_f.append(['note', tim, dur, channel, pitch, vel ])

      detailed_stats = TMIDIX.Tegridy_SONG_to_MIDI_Converter(song_f,
                                                          output_signature = 'Los Angeles Music Composer',  
                                                          output_file_name = '/content/Los-Angeles-Music-Composer-Music-Composition_'+str(i), 
                                                          track_name='Project Los Angeles',
                                                          list_of_MIDI_patches=[0, 24, 32, 40, 42, 46, 56, 71, 73, 0, 53, 19, 0, 0, 0, 0],
                                                          number_of_ticks_per_quarter=500)
      print('=' * 70)
      print('Displaying resulting composition...')
      print('=' * 70)

      fname = '/content/Los-Angeles-Music-Composer-Music-Composition_'+str(i)

      x = []
      y =[]
      c = []

      colors = ['red', 'yellow', 'green', 'cyan', 'blue', 'pink', 'orange', 'purple', 'gray', 'white', 'gold', 'silver']

      for s in song_f:
        x.append(s[1] / 1000)
        y.append(s[4])
        c.append(colors[s[3]])

      FluidSynth("/usr/share/sounds/sf2/FluidR3_GM.sf2", 16000).midi_to_audio(str(fname + '.mid'), str(fname + '.wav'))
      display(Audio(str(fname + '.wav'), rate=16000))

      plt.figure(figsize=(14,5))
      ax=plt.axes(title=fname)
      ax.set_facecolor('black')

      plt.scatter(x,y, c=c)
      plt.xlabel("Time")
      plt.ylabel("Pitch")
      plt.show()

"""# (HARMONIZE)"""

#@title Melody Harmonization

melody_instrument = "Flute" #@param ["Piano", "Guitar", "Bass", "Violin", "Cello", "Harp", "Trumpet", "Clarinet", "Flute", "Choir", "Organ"]
melody_length_in_notes = 48 #@param {type:"slider", min:16, max:512, step:16}
number_of_prime_notes = 0 #@param {type:"slider", min:0, max:32, step:1}
number_of_generation_attempts_per_melody_note = 16 #@param {type:"slider", min:1, max:64, step:1}
temperature = 1 #@param {type:"slider", min:0.1, max:1, step:0.1}

print('=' * 70)
print('Los Angeles Music Composer Advanced Melody Harmonization Model Generator')

print('=' * 70)
print('Extracting melody...')
#=======================================================

instruments_list = ["Piano", "Guitar", "Bass", "Violin", "Cello", "Harp", "Trumpet", "Clarinet", "Flute", 'Drums', "Choir", "Organ"]
melody_instrument_number = instruments_list.index(melody_instrument)

melody = []
pe = events_matrix1[0]

for e in events_matrix1:
    if e[3] != 9:

      # Cliping all values...
      tim = max(0, min(127, e[1]-pe[1]))
      dur = max(1, min(127, e[2]))
      cha = max(0, min(11, e[3]))
      ptc = max(1, min(127, e[4]))
      vel = max(8, min(127, e[5]))

      velocity = round(vel / 15)

      
      # WRITING EACH NOTE HERE
      dur_vel = (dur * 8) + (velocity-1)
      cha_ptc = (melody_instrument_number * 128) + ptc

      if tim != 0:


        melody.append([tim, dur_vel+128, cha_ptc+1152])

      pe = e

#=======================================================

print('=' * 70)
print('Melody has', len(melody), 'notes')
print('Melody has', len(melody)*4, 'tokens')

print('=' * 70)
print('Starting harmonization...')
print('=' * 70)

inp = []

for m in melody[:number_of_prime_notes]:
  inp.extend(m)

#start_time = time()
chord_time = 0

for i in tqdm.tqdm(range(number_of_prime_notes, len(melody[:melody_length_in_notes])-1)):

  next_note_time = melody[i+1][0]

  if i > 0:
    melody[i][0] = abs(melody[i][0] - pct)

  inp.extend(melody[i])

  inp = torch.LongTensor(inp).cuda()

  chord_time = 0
  count = 0

  while chord_time < next_note_time and count < number_of_generation_attempts_per_melody_note:
   
    out1 = model.module.generate(inp[None, ...], 
                          3, 
                          temperature=temperature, 
                          return_prime=False, 
                          verbose=False)
    
    inp = torch.cat((inp, out1[0]))

    pct = chord_time

    count += 1

    if out1[0][0] < 128:
      
      chord_time += out1[0][0].item()

  inp = inp[:-3].tolist()

print('=' * 70)
print('Done!')
print('=' * 70)
#print('Generation took', time() - start_time, "seconds")
print('=' * 70)

#======================================================================

print('Rendering results...')
print('=' * 70)

out1 = inp

print('Sample INTs', out1[:12])
print('=' * 70)

if len(out1) != 0:
    
    song = out1
    song_f = []
    time = 0
    dur = 0
    vel = 0
    pitch = 0
    channel = 0

    son = []
    song1 = []

    for s in song:
      if s >= 128 and s < (12*128)+1152:
        son.append(s)
      else:
        if len(son) == 3:
          song1.append(son)
        son = []
        son.append(s)
                    
    for ss in song1:

      time += ss[0] * 10

      dur = ((ss[1]-128) // 8) * 20
      vel = (((ss[1]-128) % 8)+1) * 15
   
      channel = (ss[2]-1152) // 128
      pitch = (ss[2]-1152) % 128
                      
      song_f.append(['note', time, dur, channel, pitch, vel ])

    detailed_stats = TMIDIX.Tegridy_SONG_to_MIDI_Converter(song_f,
                                                        output_signature = 'Los Angeles Music Composer',  
                                                        output_file_name = '/content/Los-Angeles-Music-Composer-Music-Composition', 
                                                        track_name='Project Los Angeles',
                                                        list_of_MIDI_patches=[0, 24, 32, 40, 42, 46, 56, 71, 73, 0, 53, 19, 0, 0, 0, 0],
                                                        number_of_ticks_per_quarter=500)


    print('=' * 70)
    print('Displaying resulting composition...')
    print('=' * 70)

    fname = '/content/Los-Angeles-Music-Composer-Music-Composition'

    x = []
    y =[]
    c = []

    colors = ['red', 'yellow', 'green', 'cyan', 'blue', 'pink', 'orange', 'purple', 'gray', 'white', 'gold', 'silver']

    for s in song_f:
      x.append(s[1] / 1000)
      y.append(s[4])
      c.append(colors[s[3]])

    FluidSynth("/usr/share/sounds/sf2/FluidR3_GM.sf2", 16000).midi_to_audio(str(fname + '.mid'), str(fname + '.wav'))
    display(Audio(str(fname + '.wav'), rate=16000))

    plt.figure(figsize=(14,5))
    ax=plt.axes(title=fname)
    ax.set_facecolor('black')

    plt.scatter(x,y, c=c)
    plt.xlabel("Time")
    plt.ylabel("Pitch")
    plt.show()

"""# Congrats! You did it! :)"""