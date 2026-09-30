import {
  ArrowLeft,
  Camera,
  CameraOff,
  CheckCircle2,
  FileImage,
  Images,
  ScanFace,
  Trash2,
  Upload,
} from "lucide-react"

import {
  useEffect,
  useRef,
  useState,
} from "react"

import {
  useNavigate,
  useParams,
} from "react-router-dom"

import {
  enrollFace,
  getFaceProfile,
  getUser,
} from "../api/smartpark"
import {
  FACE_IMAGE_TYPES,
  faceFileSignature,
  loadUserFaceState,
  MAX_FACE_IMAGES,
  MIN_FACE_IMAGES,
  validateFaceFile,
  validateFaceImageCount,
} from "../utils/faceEnrollment"


const MAX_IMAGES = MAX_FACE_IMAGES
const MIN_IMAGES = MIN_FACE_IMAGES


function FaceEnrollment() {

  const { userId } = useParams()

  const navigate = useNavigate()

  const videoRef = useRef(null)
  const streamRef = useRef(null)
  const imagesRef = useRef([])


  const [user, setUser] = useState(null)

  const [loadingUser, setLoadingUser] =
    useState(true)

  const [hasProfile, setHasProfile] =
    useState(false)

  const [userMissing, setUserMissing] = useState(false)
  const submittingRef = useRef(false)

  const [mode, setMode] =
    useState("camera")

  const [cameraActive, setCameraActive] =
    useState(false)

  const [cameraError, setCameraError] =
    useState("")

  const [images, setImages] =
    useState([])

  const [registering, setRegistering] =
    useState(false)

  const [error, setError] =
    useState("")

  const [success, setSuccess] =
    useState(null)


  /* ==========================================================
     MANTENER REFERENCIA DE LAS IMÁGENES
     ========================================================== */

  useEffect(
    () => {
      imagesRef.current = images
    },
    [images]
  )


  /* ==========================================================
     CARGAR USUARIO Y ESTADO DE BIOMETRÍA
     ========================================================== */

  useEffect(
    () => {

      async function loadData() {

        try {

          setLoadingUser(true)
          setError("")

          setUserMissing(false)
          setUser(null)
          const state = await loadUserFaceState(userId, getUser, getFaceProfile)
          setUser(state.user)
          setHasProfile(state.hasProfile)
          if (state.profileError) setError(state.profileError.message)

        } catch (err) {

          setUserMissing(err.status === 404)
          setError(err.status === 404
            ? "Usuario no encontrado. Regresa a Usuarios y verifica el registro."
            : err.message)

        } finally {

          setLoadingUser(false)

        }

      }


      loadData()

    },
    [userId]
  )


  /* ==========================================================
     LIMPIEZA AL SALIR
     ========================================================== */

  useEffect(
    () => {

      return () => {

        if (streamRef.current) {

          streamRef.current
            .getTracks()
            .forEach(
              (track) => track.stop()
            )

          streamRef.current = null

        }


        imagesRef.current.forEach(
          (item) => {

            if (item.preview) {
              URL.revokeObjectURL(
                item.preview
              )
            }

          }
        )

      }

    },
    []
  )


  /* ==========================================================
     DETENER CÁMARA
     ========================================================== */

  function stopCamera() {

    if (streamRef.current) {

      streamRef.current
        .getTracks()
        .forEach(
          (track) => track.stop()
        )

      streamRef.current = null

    }


    if (videoRef.current) {
      videoRef.current.srcObject = null
    }


    setCameraActive(false)
  }


  /* ==========================================================
     ACTIVAR CÁMARA
     ========================================================== */

  async function startCamera() {

    try {

      setCameraError("")
      setError("")


      if (
        !navigator.mediaDevices
        ||
        !navigator.mediaDevices.getUserMedia
      ) {

        setCameraError(
          "Este navegador no permite acceder a la cámara."
        )

        return
      }


      stopCamera()


      const stream =
        await navigator.mediaDevices.getUserMedia({
          video: {
            facingMode: "user",

            width: {
              ideal: 1280,
            },

            height: {
              ideal: 720,
            },
          },

          audio: false,
        })


      streamRef.current = stream


      if (videoRef.current) {

        videoRef.current.srcObject =
          stream

        await videoRef.current.play()

      }


      setCameraActive(true)

    } catch (err) {

      console.error(err)

      setCameraError(
        "No se pudo acceder a la cámara. Revisa los permisos del navegador."
      )

      setCameraActive(false)

    }
  }


  /* ==========================================================
     CAMBIAR ENTRE CÁMARA Y ARCHIVOS
     ========================================================== */

  function selectMode(nextMode) {

    setMode(nextMode)

    setError("")
    setSuccess(null)


    if (nextMode === "files") {
      stopCamera()
    }
  }


  /* ==========================================================
     CREAR ELEMENTO DE IMAGEN
     ========================================================== */

  function createImageItem(
    file,
    source
  ) {

    return {
      id:
        `${Date.now()}-${Math.random()}`,

      file,

      preview:
        URL.createObjectURL(file),

      source,
    }
  }


  /* ==========================================================
     SUBIR ARCHIVOS
     ========================================================== */

  function handleFileSelection(event) {

    if (registering || userMissing || !user) return

    const selectedFiles =
      Array.from(
        event.target.files || []
      )


    if (selectedFiles.length === 0) {
      return
    }


    setError("")
    setSuccess(null)


    const validFiles = []
    const knownFiles = new Set(images.map(({ file }) => faceFileSignature(file)))


    for (const file of selectedFiles) {

      const validationError = validateFaceFile(file, knownFiles)
      if (validationError) {
        setError(validationError)
        continue
      }
      knownFiles.add(faceFileSignature(file))
      validFiles.push(file)

    }


    const availableSlots =
      MAX_IMAGES - images.length


    if (
      validFiles.length
      >
      availableSlots
    ) {

      setError(
        `Solo puedes registrar un máximo de ${MAX_IMAGES} fotografías.`
      )
    }


    const filesToAdd =
      validFiles.slice(
        0,
        availableSlots
      )


    const newItems =
      filesToAdd.map(
        (file) =>
          createImageItem(
            file,
            "file"
          )
      )


    setImages(
      (current) => [
        ...current,
        ...newItems,
      ]
    )


    /*
     * Permite volver a seleccionar
     * el mismo archivo posteriormente.
     */

    event.target.value = ""
  }


  /* ==========================================================
     TOMAR FOTO CON LA WEBCAM
     ========================================================== */

  function capturePhoto() {

    if (registering || userMissing || !user) return

    if (!cameraActive) {

      setCameraError(
        "Primero activa la cámara."
      )

      return
    }


    if (
      images.length >= MAX_IMAGES
    ) {

      setError(
        `Ya tienes ${MAX_IMAGES} fotografías. Elimina una para tomar otra.`
      )

      return
    }


    const video =
      videoRef.current


    if (
      !video
      ||
      !video.videoWidth
      ||
      !video.videoHeight
    ) {

      setCameraError(
        "La cámara todavía no está lista. Espera un momento e inténtalo nuevamente."
      )

      return
    }


    const canvas =
      document.createElement(
        "canvas"
      )


    canvas.width =
      video.videoWidth

    canvas.height =
      video.videoHeight


    const context =
      canvas.getContext("2d")


    context.drawImage(
      video,
      0,
      0,
      canvas.width,
      canvas.height
    )


    canvas.toBlob(
      (blob) => {

        if (!blob) {

          setCameraError(
            "No se pudo capturar la fotografía."
          )

          return
        }


        const number =
          images.length + 1


        const file =
          new File(
            [blob],
            `captura-rostro-${number}.jpg`,
            {
              type: "image/jpeg",
            }
          )


        const item =
          createImageItem(
            file,
            "camera"
          )


        setImages((current) => {
          if (current.length >= MAX_IMAGES) {
            URL.revokeObjectURL(item.preview)
            return current
          }
          return [...current, item]
        })


        setError("")
        setSuccess(null)

      },
      "image/jpeg",
      0.92
    )
  }


  /* ==========================================================
     ELIMINAR FOTO
     ========================================================== */

  function removeImage(imageId) {

    if (registering) return

    setImages(
      (current) => {

        const imageToRemove =
          current.find(
            (item) =>
              item.id === imageId
          )


        if (
          imageToRemove
          &&
          imageToRemove.preview
        ) {

          URL.revokeObjectURL(
            imageToRemove.preview
          )

        }


        return current.filter(
          (item) =>
            item.id !== imageId
        )

      }
    )


    setSuccess(null)
    setError("")
  }


  /* ==========================================================
     REGISTRAR / ACTUALIZAR ROSTRO
     ========================================================== */

  async function handleEnroll() {

    if (submittingRef.current || registering || userMissing || !user) return

    const countError = validateFaceImageCount(images.length)
    if (countError) {
      setError(countError)
      return
    }


    submittingRef.current = true
    try {

      setRegistering(true)
      setError("")
      setSuccess(null)


      const wasRegistered =
        hasProfile


      const result =
        await enrollFace(
          userId,
          images.map(
            (item) => item.file
          )
        )


      setHasProfile(true)


      setSuccess({
        title: wasRegistered
          ? "Rostro actualizado correctamente"
          : "Rostro registrado correctamente",

        samples:
          result?.samples_used
          ??
          result?.samples
          ??
          images.length,

        dimension:
          result?.embedding_dimension
          ??
          result?.dimension
          ??
          null,
      })


      stopCamera()

    } catch (err) {

      setError(err.message)

    } finally {

      setRegistering(false)
      submittingRef.current = false

    }
  }


  /* ==========================================================
     LOADING
     ========================================================== */

  if (loadingUser) {

    return (
      <section>

        <div className="empty-state">
          Cargando usuario...
        </div>

      </section>
    )
  }

  if (userMissing || !user) {
    return <section>
      <div className="alert error">{error || "No se pudo cargar el usuario. Inténtalo nuevamente."}</div>
      <button className="secondary-button" type="button" onClick={() => navigate("/admin/users")}>
        <ArrowLeft size={18} /> Volver a Usuarios
      </button>
    </section>
  }


  /* ==========================================================
     INTERFAZ
     ========================================================== */

  return (
    <section>

      <div className="page-heading row-heading">

        <div>

          <p className="eyebrow">
            Biometría facial
          </p>

          <h2>
            {hasProfile
              ? "Actualizar rostro"
              : "Registrar rostro"}
          </h2>

          <p>
            Genera el perfil biométrico
            del usuario con ArcFace.
          </p>

        </div>


        <button
          className="secondary-button"
          type="button"
          onClick={
            () => {
              stopCamera()
              navigate("/admin/users")
            }
          }
        >

          <ArrowLeft size={18} />

          Volver

        </button>

      </div>


      {error && (

        <div className="alert error">
          {error}
        </div>

      )}


      <div className="face-enrollment-grid">

        {/* ====================================================
            USUARIO
            ==================================================== */}

        <div>

          <article className="panel">

            <div className="panel-header">

              <div>

                <h3>
                  Usuario
                </h3>

                <p>
                  Persona que será enrolada.
                </p>

              </div>

            </div>


            <div className="enrollment-user">

              <div className="face-user-icon">

                <ScanFace size={28} />

              </div>


              <div>

                <strong>
                  {user.name || "Nombre no disponible"}
                </strong>

                <span>
                  {user.institutional_id || "ID institucional no disponible"}
                </span>

                <span>
                  ID: {user.id ?? userId}
                </span>

              </div>

            </div>

          </article>


          <div className="face-profile-state">

            <div
              className={
                hasProfile
                  ? "profile-state-icon registered"
                  : "profile-state-icon missing"
              }
            >

              {hasProfile ? (
                <CheckCircle2 size={20} />
              ) : (
                <ScanFace size={20} />
              )}

            </div>


            <div>

              <strong>
                {hasProfile
                  ? "Biometría registrada"
                  : "Sin biometría"}
              </strong>

              <span>
                {hasProfile
                  ? "Puedes actualizar el perfil facial."
                  : "Este usuario todavía no tiene perfil facial."}
              </span>

            </div>

          </div>

        </div>


        {/* ====================================================
            REGISTRO
            ==================================================== */}

        <article className="panel">

          <div className="panel-header">

            <div>

              <h3>
                Fotografías del rostro
              </h3>

              <p>
                Utiliza entre 3 y 5 imágenes
                de buena calidad.
              </p>

            </div>

          </div>


          <div className="enrollment-form">

            {/* ================================================
                MODOS
                ================================================ */}

            <div className="enrollment-mode-tabs">

              <button
                type="button"
                disabled={registering}
                className={
                  mode === "camera"
                    ? "mode-button active"
                    : "mode-button"
                }
                onClick={
                  () =>
                    selectMode("camera")
                }
              >

                <Camera size={18} />

                Usar cámara

              </button>


              <button
                type="button"
                disabled={registering}
                className={
                  mode === "files"
                    ? "mode-button active"
                    : "mode-button"
                }
                onClick={
                  () =>
                    selectMode("files")
                }
              >

                <FileImage size={18} />

                Subir fotografías

              </button>

            </div>


            {/* ================================================
                CÁMARA
                ================================================ */}

            {mode === "camera" && (

              <div className="camera-section">

                <div className="camera-zone">

                  <video
                    ref={videoRef}
                    className={
                      cameraActive
                        ? "camera-video active"
                        : "camera-video"
                    }
                    autoPlay
                    muted
                    playsInline
                  />


                  {!cameraActive && (

                    <div className="camera-placeholder">

                      <div className="camera-placeholder-icon">

                        <Camera size={36} />

                      </div>

                      <strong>
                        Cámara desactivada
                      </strong>

                      <span>
                        Activa la cámara para
                        capturar las fotografías
                        del rostro.
                      </span>

                    </div>

                  )}


                  {cameraActive && (

                    <div className="camera-overlay">

                      <div className="face-guide" />

                    </div>

                  )}


                  {cameraActive && (

                    <div className="camera-live-badge">

                      <span />

                      Cámara activa

                    </div>

                  )}

                </div>


                {cameraError && (

                  <div className="camera-error">
                    {cameraError}
                  </div>

                )}


                <div className="camera-actions">

                  {!cameraActive ? (

                    <button
                      type="button"
                      className="primary-button camera-control-button"
                      onClick={startCamera}
                    >

                      <Camera size={18} />

                      Activar cámara

                    </button>

                  ) : (

                    <>

                      <button
                        type="button"
                        className="secondary-button camera-control-button"
                        onClick={stopCamera}
                      >

                        <CameraOff size={18} />

                        Desactivar

                      </button>


                      <button
                        type="button"
                        className="primary-button capture-button"
                        onClick={capturePhoto}
                        disabled={
                          images.length
                          >=
                          MAX_IMAGES
                        }
                      >

                        <Camera size={18} />

                        Tomar foto

                      </button>

                    </>

                  )}

                </div>


                <div className="capture-instructions">

                  <strong>
                    Recomendación para las capturas
                  </strong>

                  <p>
                    Toma una foto frontal,
                    una con ligera inclinación
                    hacia la izquierda y otra
                    hacia la derecha. Puedes
                    agregar hasta 5 imágenes.
                  </p>

                </div>

              </div>

            )}


            {/* ================================================
                ARCHIVOS
                ================================================ */}

            {mode === "files" && (

              <label className="upload-zone">

                <Upload size={34} />

                <strong>
                  Seleccionar fotografías
                </strong>

                <span>
                  Frente, ligera izquierda
                  y ligera derecha.
                </span>

                <span>
                  JPG, PNG o WEBP · Máximo 10 MB
                  por imagen
                </span>

                <input
                  type="file"
                  disabled={registering || images.length >= MAX_IMAGES}
                  accept={FACE_IMAGE_TYPES.join(",")}
                  multiple
                  onChange={
                    handleFileSelection
                  }
                />

              </label>

            )}


            {/* ================================================
                CONTADOR
                ================================================ */}

            <div className="image-counter">

              <Images size={17} />

              <span>
                {images.length}
                {" "}
                de
                {" "}
                {MAX_IMAGES}
                {" "}
                fotografías seleccionadas
              </span>

            </div>


            {/* ================================================
                IMÁGENES CAPTURADAS
                ================================================ */}

            {images.length > 0 && (

              <div className="selected-images">

                {images.map(
                  (item, index) => (

                    <div
                      className="selected-image"
                      key={item.id}
                    >

                      <div className="selected-image-info">

                        <img
                          className="selected-image-thumb"
                          src={item.preview}
                          alt={
                            `Fotografía ${index + 1}`
                          }
                        />


                        <div className="selected-image-meta">

                          <strong>
                            Foto {index + 1}
                          </strong>

                          <span>
                            {item.file.name}
                          </span>

                          <small
                            className={
                              item.source
                              ===
                              "camera"
                                ? "image-source-badge camera"
                                : "image-source-badge file"
                            }
                          >

                            {item.source
                            ===
                            "camera"
                              ? "Cámara"
                              : "Archivo"}

                          </small>

                        </div>

                      </div>


                      <button
                        type="button"
                        disabled={registering}
                        onClick={
                          () =>
                            removeImage(
                              item.id
                            )
                        }
                        aria-label={
                          `Eliminar foto ${index + 1}`
                        }
                      >

                        <Trash2 size={17} />

                      </button>

                    </div>

                  )
                )}

              </div>

            )}


            {/* ================================================
                RECOMENDACIÓN
                ================================================ */}

            <div className="enrollment-help">

              <strong>
                Recomendación
              </strong>

              <p>
                Usa fotografías con buena
                iluminación, una sola persona,
                sin desenfoque y con pequeñas
                variaciones del ángulo del
                rostro.
              </p>

            </div>


            {/* ================================================
                ÉXITO
                ================================================ */}

            {success && (

              <div className="enrollment-success">

                <CheckCircle2 size={24} />

                <div>

                  <strong>
                    {success.title}
                  </strong>

                  <span>
                    {user.name || "Usuario"}
                    {" · "}
                    {success.samples}
                    {" "}
                    fotos
                    {success.dimension ? ` · ${success.dimension}D` : ""}
                  </span>

                </div>

              </div>

            )}


            {/* ================================================
                BOTÓN FINAL
                ================================================ */}

            <button
              type="button"
              className="primary-button enroll-button"
              onClick={handleEnroll}
              disabled={
                registering
                ||
                images.length < MIN_IMAGES
                ||
                images.length > MAX_IMAGES
              }
            >

              <ScanFace size={19} />

              {registering
                ? "Procesando rostro..."
                : hasProfile
                  ? "Actualizar rostro"
                  : "Registrar rostro"}

            </button>

          </div>

        </article>

      </div>

    </section>
  )
}


export default FaceEnrollment
