import os

from deepface import DeepFace

from app.models import Student, FaceData


def recognize_student(image_path):
    """
    Compare the captured face against registered student faces.

    Returns:

        {
            "success": True,
            "student": student,
            "distance": distance,
            "message": "..."
        }

    OR

        {
            "success": False,
            "student": None,
            "distance": None,
            "message": "..."
        }
    """

    try:

        # =====================================================
        # 1. CHECK CAPTURED IMAGE
        # =====================================================

        if not image_path:

            return {
                "success": False,
                "student": None,
                "distance": None,
                "message": "No image was provided."
            }


        if not os.path.exists(image_path):

            return {
                "success": False,
                "student": None,
                "distance": None,
                "message": "Captured image could not be found."
            }


        # =====================================================
        # 2. GET REGISTERED FACE DATA
        # =====================================================

        face_records = FaceData.query.all()


        if not face_records:

            return {
                "success": False,
                "student": None,
                "distance": None,
                "message": "No registered faces are available."
            }


        # =====================================================
        # 3. COMPARE WITH REGISTERED STUDENTS
        # =====================================================

        best_student = None

        best_distance = None


        for face_record in face_records:

            registered_image = face_record.image_path


            if not registered_image:

                continue


            # -------------------------------------------------
            # Convert relative path to absolute path
            # -------------------------------------------------

            if not os.path.isabs(
                registered_image
            ):

                registered_image = os.path.abspath( registered_image
                )


            if not os.path.exists(  registered_image
            ):

                print(
                    "Registered face not found:",
                    registered_image
                )

                continue


            # -------------------------------------------------
            # DeepFace verification
            # -------------------------------------------------

            try:

                result = DeepFace.verify(

                    img1_path=image_path,

                    img2_path=registered_image,

                    model_name="Facenet512",

                    detector_backend="opencv",

                    distance_metric="cosine",

                    enforce_detection=True,

                    align=True

                )


                verified = result.get(
                    "verified",
                    False
                )


                distance = result.get(
                    "distance"
                )


                threshold = result.get(
                    "threshold"
                )


                print(
                    "Comparing:",
                    registered_image
                )

                print(
                    "Verified:",
                    verified
                )

                print(
                    "Distance:",
                    distance
                )

                print(
                    "Threshold:",
                    threshold
                )


                if verified:

                    if (
                        best_distance is None
                        or distance < best_distance
                    ):

                        best_distance = distance

                        best_student = (
                            Student.query.get(
                                face_record.student_id
                            )
                        )


            except Exception as verification_error:

                print(
                    "Verification error:",
                    verification_error
                )

                continue


        # =====================================================
        # 4. STUDENT FOUND
        # =====================================================

        if best_student:

            return {

                "success": True,

                "student": best_student,

                "distance": best_distance,

                "message":
                    f"Student recognized: "
                    f"{best_student.name}"

            }


        # =====================================================
        # 5. STUDENT NOT FOUND
        # =====================================================

        return {

            "success": False,

            "student": None,

            "distance": None,

            "message":
                "Face not recognized. "
                "Please register the student first."

        }


    except Exception as error:

        print(
            "Recognition error:",
            error
        )


        return {

            "success": False,

            "student": None,

            "distance": None,

            "message":
                f"Face recognition failed: {error}"

        }