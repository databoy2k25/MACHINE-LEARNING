import cv2
from deepface import DeepFace


def detect_face(image_path):

    try:

        # =====================================================
        # 1. READ IMAGE
        # =====================================================

        image = cv2.imread(image_path)

        if image is None:

            return (
                False,
                "Unable to read the captured image."
            )


        # =====================================================
        # 2. CHECK IMAGE SIZE
        # =====================================================

        height, width = image.shape[:2]

        print(
            f"Image size: {width} x {height}"
        )


        if width < 200 or height < 200:

            return (
                False,
                "Image resolution is too small. Please capture the face again."
            )


        # =====================================================
        # 3. DEEPFACE FACE DETECTION
        # =====================================================

        print(
            "Running DeepFace face detection..."
        )


        try:

            faces = DeepFace.extract_faces(

                img_path=image_path,

                detector_backend="opencv",

                enforce_detection=True,

                align=True

            )


            print(
                "DeepFace detected faces:",
                len(faces)
            )


        except Exception as deepface_error:

            print(
                "DeepFace detection error:",
                deepface_error
            )


            return (
                False,
                "No face detected. Please look directly at the camera and make sure your face is clearly visible."
            )


        # =====================================================
        # 4. CHECK FACE COUNT
        # =====================================================

        if not faces:

            return (
                False,
                "No face detected. Please look directly at the camera."
            )


        if len(faces) > 1:

            return (
                False,
                "Multiple faces detected. Please register only one person."
            )


        # =====================================================
        # 5. BASIC OPENCV VALIDATION
        # =====================================================

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )


        # Calculate average brightness

        brightness = gray.mean()


        print(
            "Image brightness:",
            brightness
        )


        if brightness < 25:

            return (
                False,
                "Image is too dark. Please improve the lighting."
            )


        if brightness > 245:

            return (
                False,
                "Image is too bright. Please reduce the lighting."
            )


        # =====================================================
        # 6. SUCCESS
        # =====================================================

        print(
            "Face detected successfully."
        )


        return (
            True,
            "Face detected and registered successfully."
        )


    except Exception as error:

        print(
            "Face detection error:",
            error
        )


        return (
            False,
            f"Face detection failed: {error}"
        )