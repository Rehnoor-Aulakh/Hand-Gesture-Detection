import cv2
import mediapipe as mp
from pynput.keyboard import Controller,Key

#Creating object of Controller class, that helps to map keyboard with actions
keyboard=Controller()

mp_hands=mp.solutions.hands
mp_drawing=mp.solutions.drawing_utils

#Creating object of Hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

tip_ids=[4,8,12,16,20]


cap=cv2.VideoCapture(0)
prev_keys=set()

def release_all_keys():
    for k in prev_keys:
        try:
            keyboard.release(k)
        except:
            pass

def press_key(keys):
    global prev_keys
    release_all_keys()
    for k in keys:
        try:
            keyboard.press(k)
        except Exception as e:
            print(f"Error pressing {k}: {e}")
    prev_keys = set(keys)


while cap.isOpened():
    success,frame=cap.read()
    if not success:
        break
    
    frame=cv2.flip(frame,1)
    rgb_frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
    
    #Process the frame
    results=hands.process(rgb_frame)
    
    keys_to_press=[]
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame,hand_landmarks,mp_hands.HAND_CONNECTIONS)    
            lm_list=[]
            for id,lm in enumerate(hand_landmarks.landmark):
                h,w,_=frame.shape
                lm_list.append((int(lm.x * w), int(lm.y * h)))
                
            fingers=[]
            
            #Thumb- check X axis difference
            if lm_list[tip_ids[0]][0]>lm_list[tip_ids[0]-2][0]:
                fingers.append(0)
            else:
                fingers.append(1)
                
            #for other fingers
            for i in range(1,5):
                if lm_list[tip_ids[i]][1]<lm_list[tip_ids[i]-2][1]:
                    fingers.append(1)
                else:
                    fingers.append(0)
                    
            print("Fingers Up: ",fingers)
            
            if fingers[1]:
                keys_to_press.append('w') 
            if fingers[0]:
                keys_to_press.append('a')
            if fingers[2]:
                keys_to_press.append('d')
            if fingers[4]:
                keys_to_press.append(Key.shift)
            if sum(fingers)==0:
                keys_to_press.append(Key.space)
                
            if set(keys_to_press)!=prev_keys:
                press_key(keys_to_press)
                print("Pressed keys: ",keys_to_press)
    else:
        if prev_keys:
            release_all_keys()
            prev_keys=set()
    
    cv2.imshow("HandTracking",frame)
    if cv2.waitKey(1) & 0xFF==27:
        break
    
cap.release()
cv2.destroyAllWindows()