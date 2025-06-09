import streamlit as st
import cv2
import numpy as np
import dlib
import imutils

# Load models
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")  # Download from: http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2

def get_landmarks(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    if len(faces) == 0:
        return None
    return np.matrix([[p.x, p.y] for p in predictor(gray, faces[0]).parts()])

def transformation_matrix(points1, points2):
    points1 = np.float32(points1)
    points2 = np.float32(points2)
    return cv2.getAffineTransform(points1[:3], points2[:3])

def warp_triangle(img1, img2, t1, t2):
    r1 = cv2.boundingRect(np.float32([t1]))
    r2 = cv2.boundingRect(np.float32([t2]))

    t1_rect = []
    t2_rect = []
    t2_rect_int = []

    for i in range(3):
        t1_rect.append(((t1[i][0] - r1[0]), (t1[i][1] - r1[1])))
        t2_rect.append(((t2[i][0] - r2[0]), (t2[i][1] - r2[1])))
        t2_rect_int.append(((t2[i][0] - r2[0]), (t2[i][1] - r2[1])))

    img1_rect = img1[r1[1]:r1[1]+r1[3], r1[0]:r1[0]+r1[2]]
    size = (r2[2], r2[3])

    warp_mat = cv2.getAffineTransform(np.float32(t1_rect), np.float32(t2_rect))
    img2_rect = cv2.warpAffine(img1_rect, warp_mat, size, None, flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)

    mask = np.zeros((r2[3], r2[2], 3), dtype=np.float32)
    cv2.fillConvexPoly(mask, np.int32(t2_rect_int), (1.0, 1.0, 1.0), 16, 0)

    img2[r2[1]:r2[1]+r2[3], r2[0]:r2[0]+r2[2]] = img2[r2[1]:r2[1]+r2[3], r2[0]:r2[0]+r2[2]] * (1 - mask) + img2_rect * mask

def face_swap(img1, img2):
    landmarks1 = get_landmarks(img1)
    landmarks2 = get_landmarks(img2)

    if landmarks1 is None or landmarks2 is None:
        return None

    img2_warped = np.copy(img2)

    hull1 = []
    hull2 = []
    hullIndex = cv2.convexHull(landmarks2, returnPoints=False)

    for i in range(0, len(hullIndex)):
        hull1.append(landmarks1[hullIndex[i][0]])
        hull2.append(landmarks2[hullIndex[i][0]])

    hull1 = np.array(hull1, dtype=np.int32)
    hull2 = np.array(hull2, dtype=np.int32)

    # Triangulate
    rect = cv2.boundingRect(hull2)
    subdiv = cv2.Subdiv2D(rect)
    subdiv.insert([tuple(p[0]) for p in hull2])
    triangles = subdiv.getTriangleList()
    triangles = np.array(triangles, dtype=np.int32)

    for t in triangles:
        pt1 = (t[0], t[1])
        pt2 = (t[2], t[3])
        pt3 = (t[4], t[5])

        index1 = np.where((hull2[:, 0] == pt1[0]) & (hull2[:, 1] == pt1[1]))[0]
        index2 = np.where((hull2[:, 0] == pt2[0]) & (hull2[:, 1] == pt2[1]))[0]
        index3 = np.where((hull2[:, 0] == pt3[0]) & (hull2[:, 1] == pt3[1]))[0]

        if len(index1) and len(index2) and len(index3):
            t1 = [hull1[index1[0]][0], hull1[index2[0]][0], hull1[index3[0]][0]]
            t2 = [hull2[index1[0]][0], hull2[index2[0]][0], hull2[index3[0]][0]]

            warp_triangle(img1, img2_warped, t1, t2)

    return img2_warped

# Streamlit UI
st.title("🧑‍🤝‍🧑 AI Face Swap with Streamlit")

img1 = st.file_uploader("Upload Source Face Image", type=['jpg', 'jpeg', 'png'])
img2 = st.file_uploader("Upload Target Image", type=['jpg', 'jpeg', 'png'])

if img1 and img2:
    image1 = cv2.imdecode(np.frombuffer(img1.read(), np.uint8), 1)
    image2 = cv2.imdecode(np.frombuffer(img2.read(), np.uint8), 1)

    swapped = face_swap(image1, image2)

    if swapped is not None:
        st.image(swapped, caption="Face Swapped Output", channels="BGR")
        result = cv2.imencode(".jpg", swapped)[1].tobytes()
        st.download_button("Download Result", result, "face_swapped.jpg", "image/jpeg")
    else:
        st.error("Could not detect face in one of the images.")