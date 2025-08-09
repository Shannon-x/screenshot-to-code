import { useState, useEffect, useMemo } from "react";
import { useDropzone } from "react-dropzone";
import { toast } from "react-hot-toast";
import { URLS } from "../urls";
import ScreenRecorder from "./recording/ScreenRecorder";
import { ScreenRecorderState } from "../types";
import { useLocale } from "../hooks/useLocale";

const baseStyle = {
  flex: 1,
  width: "80%",
  margin: "0 auto",
  minHeight: "400px",
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  justifyContent: "center",
  padding: "20px",
  borderWidth: 2,
  borderRadius: 2,
  borderColor: "#eeeeee",
  borderStyle: "dashed",
  backgroundColor: "#fafafa",
  color: "#bdbdbd",
  outline: "none",
  transition: "border .24s ease-in-out",
};

const focusedStyle = {
  borderColor: "#2196f3",
};

const acceptStyle = {
  borderColor: "#00e676",
};

const rejectStyle = {
  borderColor: "#ff1744",
};

// TODO: Move to a separate file
function fileToDataURL(file: File) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = (error) => reject(error);
    reader.readAsDataURL(file);
  });
}

type FileWithPreview = {
  preview: string;
} & File;

interface Props {
  setReferenceImages: (
    referenceImages: string[],
    inputMode: "image" | "video"
  ) => void;
}

function ImageUpload({ setReferenceImages }: Props) {
  const [files, setFiles] = useState<FileWithPreview[]>([]);
  const [screenRecorderState, setScreenRecorderState] =
    useState<ScreenRecorderState>(ScreenRecorderState.INITIAL);
  const { t } = useLocale();

  const { getRootProps, getInputProps, isFocused, isDragAccept, isDragReject } =
    useDropzone({
      maxFiles: 1,
      maxSize: 1024 * 1024 * 20, // 20 MB
      accept: {
        // Image formats
        "image/png": [".png"],
        "image/jpeg": [".jpeg"],
        "image/jpg": [".jpg"],
        // Video formats
        "video/quicktime": [".mov"],
        "video/mp4": [".mp4"],
        "video/webm": [".webm"],
      },
      onDrop: (acceptedFiles) => {
        // Set up the preview thumbnail images
        setFiles(
          acceptedFiles.map((file: File) =>
            Object.assign(file, {
              preview: URL.createObjectURL(file),
            })
          ) as FileWithPreview[]
        );

        // Convert images to data URLs and set the prompt images state
        Promise.all(acceptedFiles.map((file) => fileToDataURL(file)))
          .then((dataUrls) => {
            if (dataUrls.length > 0) {
              setReferenceImages(
                dataUrls.map((dataUrl) => dataUrl as string),
                (dataUrls[0] as string).startsWith("data:video")
                  ? "video"
                  : "image"
              );
            }
          })
          .catch((error) => {
            toast.error(t("errors.imageUploadFailed") + ": " + error);
            console.error("Error reading files:", error);
          });
      },
      onDropRejected: (rejectedFiles) => {
        const error = rejectedFiles[0].errors[0];
        if (error.code === "file-too-large") {
          toast.error(t("errors.imageTooLarge"));
        } else if (error.code === "file-invalid-type") {
          toast.error(t("errors.invalidImageFormat"));
        } else {
          toast.error(error.message);
        }
      },
    });

  useEffect(() => {
    return () => files.forEach((file) => URL.revokeObjectURL(file.preview));
  }, [files]);

  const style = useMemo(
    () => ({
      ...baseStyle,
      ...(isFocused ? focusedStyle : {}),
      ...(isDragAccept ? acceptStyle : {}),
      ...(isDragReject ? rejectStyle : {}),
    }),
    [isFocused, isDragAccept, isDragReject]
  );

  return (
    <section className="container">
      {screenRecorderState === ScreenRecorderState.INITIAL && (
        /* eslint-disable-next-line @typescript-eslint/no-explicit-any */
        <div {...getRootProps({ style: style as any })}>
          <input {...getInputProps()} className="file-input" />
          <p className="text-slate-700 text-lg text-center">
            {t("main.dragDropHint")}
          </p>
          <p className="text-slate-600 text-sm mt-2">
            {t("main.pasteHint")}
          </p>
        </div>
      )}
      {screenRecorderState === ScreenRecorderState.INITIAL && (
        <div className="text-center text-sm text-slate-800 mt-4">
          支持上传屏幕录像（.mp4、.mov）或录制屏幕来克隆整个应用（实验性功能）。{" "}
          <a
            className="underline"
            href={URLS["intro-to-video"]}
            target="_blank"
          >
            了解更多
          </a>
        </div>
      )}
      <ScreenRecorder
        screenRecorderState={screenRecorderState}
        setScreenRecorderState={setScreenRecorderState}
        generateCode={setReferenceImages}
      />
    </section>
  );
}

export default ImageUpload;