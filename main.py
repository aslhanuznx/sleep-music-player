import cv2
import mediapipe as mp
import pygame
import math
import time


# ======================
# SES
# ======================

pygame.init()
pygame.mixer.init()

pygame.mixer.music.load("uyan_yegen.mp3")

music_playing = False


# ======================
# MEDIAPIPE
# ======================

mp_face_mesh = mp.solutions.face_mesh

face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True
)


# ======================
# KAMERA
# ======================

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,720)


# ======================
# GÖZ NOKTALARI
# ======================

LEFT_EYE = [33,160,158,133,153,144]
RIGHT_EYE = [362,385,387,263,373,380]


def distance(a,b):

    return math.sqrt(
        (a.x-b.x)**2 +
        (a.y-b.y)**2
    )


def eye_ratio(points,eye):

    p1=points[eye[0]]
    p2=points[eye[1]]
    p3=points[eye[2]]
    p4=points[eye[3]]
    p5=points[eye[4]]
    p6=points[eye[5]]

    vertical = distance(p2,p6)+distance(p3,p5)
    horizontal = distance(p1,p4)

    return vertical/(2*horizontal)



# ======================
# DURUMLAR
# ======================

closed_frames = 0
alarm_count = 0
start_closed = None



# ======================
# ANA DÖNGÜ
# ======================

while True:


    ret,frame = cap.read()


    if not ret:
        break



    h,w,_ = frame.shape


    rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )


    result = face_mesh.process(rgb)



    if result.multi_face_landmarks:


        face = result.multi_face_landmarks[0]



        # ======================
        # YÜZ KUTUSU
        # ======================

        xs=[]
        ys=[]


        for p in face.landmark:

            xs.append(int(p.x*w))
            ys.append(int(p.y*h))


        x1=min(xs)
        y1=min(ys)
        x2=max(xs)
        y2=max(ys)



        cv2.rectangle(
            frame,
            (x1-20,y1-20),
            (x2+20,y2+20),
            (0,255,0),
            2
        )



        # ======================
        # GÖZ TAKİP
        # ======================


        left = eye_ratio(
            face.landmark,
            LEFT_EYE
        )


        right = eye_ratio(
            face.landmark,
            RIGHT_EYE
        )


        avg = (left+right)/2



        # ======================
        # KIRMIZI GÖZ KARESİ
        # ======================

        eye_x = int(face.landmark[468].x*w)
        eye_y = int(face.landmark[468].y*h)


        box_size = 18


        cv2.rectangle(
            frame,
            (
                eye_x-box_size,
                eye_y-box_size
            ),
            (
                eye_x+box_size,
                eye_y+box_size
            ),
            (0,0,255),
            2
        )


        cv2.circle(
            frame,
            (eye_x,eye_y),
            3,
            (0,0,255),
            -1
        )



        # ======================
        # GÖZ KAPALI KONTROL
        # ======================


        if avg < 0.20:

            closed_frames += 1


            if start_closed is None:
                start_closed=time.time()


        else:

            closed_frames=0
            start_closed=None


            if music_playing:

                pygame.mixer.music.stop()
                music_playing=False



        # ======================
        # ALARM
        # ======================


        if closed_frames > 20:


            overlay=frame.copy()


            cv2.rectangle(
                overlay,
                (0,0),
                (w,h),
                (0,0,255),
                -1
            )


            frame=cv2.addWeighted(
                overlay,
                0.35,
                frame,
                0.65,
                0
            )


            if not music_playing:

                pygame.mixer.music.play(-1)

                music_playing=True

                alarm_count+=1



            size=int(
                1.5+
                abs(math.sin(time.time()*3))
            )


            cv2.putText(
                frame,
                "UYAN YEGEN!",
                (300,350),
                cv2.FONT_HERSHEY_DUPLEX,
                size,
                (255,255,255),
                4
            )


        else:


            cv2.putText(
                frame,
                "TARGET LOCKED",
                (20,80),
                cv2.FONT_HERSHEY_DUPLEX,
                1,
                (0,255,0),
                2
            )



        # ======================
        # HUD PANEL
        # ======================


        cv2.rectangle(
            frame,
            (10,10),
            (270,150),
            (30,30,30),
            -1
        )


        cv2.putText(
            frame,
            "KAMERA : AKTIF",
            (20,40),
            cv2.FONT_HERSHEY_SIMPLEX,
            .7,
            (0,255,0),
            2
        )


        cv2.putText(
            frame,
            f"GOZ : {avg:.2f}",
            (20,75),
            cv2.FONT_HERSHEY_SIMPLEX,
            .7,
            (255,255,255),
            2
        )


        cv2.putText(
            frame,
            f"ALARM : {alarm_count}",
            (20,110),
            cv2.FONT_HERSHEY_SIMPLEX,
            .7,
            (0,255,255),
            2
        )



    cv2.imshow(
        "Goz Takibi",
        frame
    )



    key=cv2.waitKey(1)&0xff


    if key==27 or key==ord("q"):

        break



cap.release()
cv2.destroyAllWindows()
pygame.quit()