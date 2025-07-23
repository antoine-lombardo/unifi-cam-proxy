class CameraModelDatabase:
    CameraPlatformsByType = {
        # Early cameras
        "UVC": "s2l",
        "UVC_PRO": "s2l",
        "UVC_DOME": "s2l",
        "UVC_MICRO": "s2l",

        # G3 Series
        "UVC_G3": "s2lm",
        "UVC_G3_DOME": "s2lm",
        "UVC_G3_MICRO": "s2lm",
        "UVC_G3_MINI": "s2lm",
        "UVC_G3_INSTANT": "s2lm",
        "UVC_G3_PRO": "s2lm",
        "UVC_G3_FLEX": "s2lm",

        # G4 Series
        "UVC_G4_BULLET": "s5l",
        "UVC_G4_PRO": "s5l",
        "UVC_G4_PTZ": "s5l",
        "UVC_G4_DOME": "s5l",
        "UVC_G4_INSTANT": "cv22",
        "UVC_G4_DOORBELL": "cv22",
        "UVC_G4_DOORBELL_PRO": "cv25z",
        "UVC_G4_DOORBELL_PRO_WHITE": "cv25z",
        "UVC_G4_DOORBELL_PRO_POE": "cv25z",
        "UVC_G4_DOORBELL_PRO_POE_WHITE": "cv25z",

        # G5 Series
        "UVC_G5_BULLET": "cv2x",
        "UVC_G5_DOME": "cv2x",
        "UVC_G5_FLEX": "cv2x",
        "UVC_G5_PRO": "cv2x",
        "UVC_G5_PTZ": "cv2x",
        "UVC_G5_DOME_ULTRA": "cv2x",
        "UVC_G5_DOME_ULTRA_BLACK": "cv2x",
        "UVC_G5_TURRET_ULTRA": "cv2x",
        "UVC_G5_TURRET_ULTRA_BLACK": "cv2x",

        # G6 Series
        "UVC_G6_BULLET": "cv2x",
        "UVC_G6_BULLET_BLACK": "cv2x",
        "UVC_G6_DOME": "cv2x",
        "UVC_G6_DOME_BLACK": "cv2x",
        "UVC_G6_TURRET": "cv2x",
        "UVC_G6_TURRET_BLACK": "cv2x",
        "UVC_G6_INSTANT": "cv2x",
        "UVC_G6_PTZ": "cv2x",
        "UVC_G6_PTZ_BLACK": "cv2x",
        "UVC_G6_PRO_360": "cv2x",
        "UVC_G6_PRO_360_BLACK": "cv2x",
        "UVC_G6_PRO_BULLET": "cv2x",
        "UVC_G6_180": "cv2x",

        # AI Series
        "UVC_AI_360": "cv25z",
        "UVC_AI_360_WHITE": "cv25z",
        "UVC_AI_BULLET": "cv25z",
        "UVC_AI_DSLR": "cv25z",
        "UVC_AI_PRO": "cv25z",
        "UVC_AI_PRO_WHITE": "cv25z",
        "UVC_AI_PRO_LPR": "cv25z",
        "UVC_AI_LPR": "cv25z",
        "UVC_AI_THETA": "cv25z",
        "UVC_AI_DOME": "cv25z",
        "UVC_AI_TURRET": "cv25z",
        "UVC_AI_PTZ": "cv25z",
        "UVC_AI_PTZ_WHITE": "cv25z",
        "UVC_AI_PTZ_PRECISION": "cv25z",
        "UVC_AI_PTZ_PRECISION_WHITE": "cv25z",

        # Doorbell Lite
        "UVC_DOORBELL_LITE": "cv22",
        "UVC_DOORBELL_LITE_WHITE": "cv22",

        # Other
        "AFI_VC": "s2l",
        "VISION_PRO": "cv25z"
    }

    CameraSysIds = {
        "AFI_VC": 0xa553,
        "UVC": 0xa524,
        "UVC_AI_360": 0xa5a0,
        "UVC_AI_BULLET": 0xa5a2,
        "UVC_AI_THETA": 0xa5a3,
        "UVC_AI_DSLR": 0xa5b0,
        "UVC_AI_PRO": 0xa5a4,
        "UVC_AI_DOME": 0xa5a5,
        "UVC_AI_TURRET": 0xa5a6,
        "UVC_AI_LPR": 0xa5a7,
        "UVC_DOME": 0xa525,
        "UVC_G3": 0xa531,
        "UVC_G3_DOME": 0xa533,
        "UVC_G3_FLEX": 0xa534,
        "UVC_G3_MICRO": 0xa552,
        "UVC_G3_INSTANT": 0xa590,
        "UVC_G3_PRO": 0xa532,
        "UVC_G4_PRO": 0xa563,
        "UVC_G4_PTZ": 0xa564,
        "UVC_G4_DOORBELL": 0xa571,
        "UVC_G4_DOORBELL_PRO": 0xa574,
        "UVC_G4_DOORBELL_PRO_WHITE": 0xa576,
        "UVC_G4_DOORBELL_PRO_POE": 0xa575,
        "UVC_G4_BULLET": 0xa572,
        "UVC_G4_DOME": 0xa573,
        "UVC_G4_INSTANT": 0xa595,
        "UVC_G5_BULLET": 0xa591,
        "UVC_G5_DOME": 0xa592,
        "UVC_G5_FLEX": 0xa593,
        "UVC_G5_PRO": 0xa598,
        "UVC_G5_PTZ": 0xa59b,
        "UVC_G5_DOME_ULTRA": 0xa59d,
        "UVC_G5_TURRET_ULTRA": 0xa59c,
        "UVC_MICRO": 0xa526,
        "UVC_PRO": 0xa521,
        "VISION_PRO": 0xa551,
        "UVC_G6_BULLET": 0xa600,
        "UVC_G6_BULLET_BLACK": 0xa06a,
        "UVC_G6_TURRET": 0xa601,
        "UVC_G6_TURRET_BLACK": 0xa06b,
        "UVC_G6_DOME": 0xa602,
        "UVC_G6_DOME_BLACK": 0xa06c,
        "UVC_G6_INSTANT": 0xa603,
        "UVC_AI_PTZ": 0xa604,
        "UVC_AI_PTZ_WHITE": 0xa065,
        "UVC_G6_PTZ": 0xa605,
        "UVC_G6_PTZ_BLACK": 0xa606,
        "UVC_DOORBELL_LITE": 0xa061,
        "UVC_DOORBELL_LITE_WHITE": 0xa062,
        "UVC_G6_PRO_360": 0xa60f,
        "UVC_G6_PRO_360_BLACK": 0xa060,
        "UVC_G6_PRO_BULLET": 0xa607,
        "UVC_G6_180": 0xa60e,
        "UVC_AI_PTZ_PRECISION": 0xa067,
        "UVC_AI_PTZ_PRECISION_WHITE": 0xa066,
    }

    # End-of-life cameras
    EOLCameraTypes = [
        "UVC",
        "UVC_PRO",
        "UVC_DOME",
        "UVC_MICRO"
    ]

    @classmethod
    def get_platform(cls, model_name):
        return cls.CameraPlatformsByType.get(model_name)
