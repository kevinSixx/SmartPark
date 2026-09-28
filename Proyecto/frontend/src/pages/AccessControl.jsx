import {
  Camera,
  CameraOff,
  Car,
  CheckCircle2,
  LogIn,
  LogOut,
  RotateCcw,
  ScanFace,
  ShieldCheck,
  ShieldX,
} from "lucide-react"

import {
  useEffect,
  useRef,
  useState,
} from "react"

import {
  processAccess,
} from "../api/smartpark"


function AccessControl() {

  const videoRef =
    useRef(null)

  const streamRef =
    useRef(null)

  const faceRef =
    useRef(null)

  const plateRef =
    useRef(null)


  const [cameraActive, setCameraActive] =
    useState(false)

  const [cameraError, setCameraError] =
    useState("")


  const [eventType, setEventType] =
    useState("ENTRY")


  const [faceCapture, setFaceCapture] =
    useState(null)

  const [plateCapture, setPlateCapture] =
    useState(null)


  const [processing, setProcessing] =
    useState(false)

  const [error, setError] =
    useState("")

  const [result, setResult] =
    useState(null)


  /* ==========================================================
     REFERENCIAS CAPTURAS
     ========================================================== */

  useEffect(
    () => {

      faceRef.current =
        faceCapture

    },
    [faceCapture]
  )


  useEffect(
    () => {

      plateRef.current =
        plateCapture

    },
    [plateCapture]
  )


  /* ==========================================================
     LIMPIEZA
     ========================================================== */

  useEffect(
    () => {

      return () => {

        if (streamRef.current) {

          streamRef.current
            .getTracks()
            .forEach(
              (track) =>
                track.stop()
            )

        }


        if (
          faceRef.current?.preview
        ) {

          URL.revokeObjectURL(
            faceRef.current.preview
          )

        }


        if (
          plateRef.current?.preview
        ) {

          URL.revokeObjectURL(
            plateRef.current.preview
          )

        }

      }

    },
    []
  )


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
          "Este navegador no permite utilizar la cámara."
        )

        return
      }


      stopCamera()


      const stream =
        await navigator.mediaDevices
          .getUserMedia({
            video: {
              width: {
                ideal:
                  1280,
              },

              height: {
                ideal:
                  720,
              },

              facingMode: {
                ideal:
                  "environment",
              },
            },

            audio:
              false,
          })


      streamRef.current =
        stream


      if (
        videoRef.current
      ) {

        videoRef.current.srcObject =
          stream

        await videoRef.current.play()

      }


      setCameraActive(
        true
      )


    } catch (err) {

      console.error(err)

      setCameraActive(
        false
      )

      setCameraError(
        "No se pudo acceder a la cámara. Revisa los permisos del navegador."
      )

    }
  }


  /* ==========================================================
     DETENER CÁMARA
     ========================================================== */

  function stopCamera() {

    if (
      streamRef.current
    ) {

      streamRef.current
        .getTracks()
        .forEach(
          (track) =>
            track.stop()
        )

      streamRef.current =
        null

    }


    if (
      videoRef.current
    ) {

      videoRef.current.srcObject =
        null

    }


    setCameraActive(
      false
    )
  }


  /* ==========================================================
     CAPTURAR FRAME
     ========================================================== */

  function captureFrame(
    type
  ) {

    if (
      !cameraActive
    ) {

      setCameraError(
        "Primero activa la cámara."
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
        "La cámara todavía no está lista."
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
      canvas.getContext(
        "2d"
      )


    /*
     * Importante:
     * El video puede verse espejado en pantalla,
     * pero el frame enviado se conserva normal.
     * Esto es importante para OCR de placas.
     */

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

          setError(
            "No se pudo capturar la imagen."
          )

          return
        }


        const fileName =
          type === "face"
            ? "smartpark-face.jpg"
            : "smartpark-plate.jpg"


        const file =
          new File(
            [blob],
            fileName,
            {
              type:
                "image/jpeg",
            }
          )


        const capture = {
          file,

          preview:
            URL.createObjectURL(
              file
            ),
        }


        if (
          type === "face"
        ) {

          if (
            faceCapture?.preview
          ) {

            URL.revokeObjectURL(
              faceCapture.preview
            )
          }


          setFaceCapture(
            capture
          )

        } else {

          if (
            plateCapture?.preview
          ) {

            URL.revokeObjectURL(
              plateCapture.preview
            )
          }


          setPlateCapture(
            capture
          )

        }


        setResult(
          null
        )

        setError(
          ""
        )

      },

      "image/jpeg",
      0.92
    )
  }


  /* ==========================================================
     LIMPIAR CAPTURAS
     ========================================================== */

  function resetCaptures() {

    if (
      faceCapture?.preview
    ) {

      URL.revokeObjectURL(
        faceCapture.preview
      )
    }


    if (
      plateCapture?.preview
    ) {

      URL.revokeObjectURL(
        plateCapture.preview
      )
    }


    setFaceCapture(
      null
    )

    setPlateCapture(
      null
    )

    setResult(
      null
    )

    setError(
      ""
    )
  }


  /* ==========================================================
     PROCESAR ACCESO
     ========================================================== */

  async function handleProcess() {

    if (
      !faceCapture
    ) {

      setError(
        "Captura primero el rostro."
      )

      return
    }


    if (
      !plateCapture
    ) {

      setError(
        "Captura primero la placa."
      )

      return
    }


    try {

      setProcessing(
        true
      )

      setError(
        ""
      )

      setResult(
        null
      )


      const response =
        await processAccess(
          faceCapture.file,
          plateCapture.file,
          eventType
        )


      setResult(
        response
      )


    } catch (err) {

      setError(
        err.message
      )

    } finally {

      setProcessing(
        false
      )

    }
  }


  /* ==========================================================
     DATOS DEL RESULTADO
     ========================================================== */

  const authorization =
    result?.authorization
    ||
    {}


  const decision =
    (
      authorization.decision
      ||
      result?.decision
      ||
      ""
    )
      .toString()
      .toUpperCase()


  const authorized =
    decision ===
    "AUTHORIZED"


  const denied =
    decision ===
    "DENIED"
    ||
    decision ===
    "REJECTED"


  const person =
    result?.person
    ||
    authorization.user_name
    ||
    authorization.name
    ||
    "No identificado"


  const detectedPlate =
    result?.plate_display
    ||
    result?.detected_plate
    ||
    "No detectada"


  const reason =
    authorization.reason
    ||
    result?.reason
    ||
    "—"


  function formatScore(
    value
  ) {

    if (
      value === null
      ||
      value === undefined
    ) {

      return "—"
    }


    const number =
      Number(value)


    if (
      Number.isNaN(number)
    ) {

      return "—"
    }


    const percentage =
      number <= 1
        ? number * 100
        : number


    return (
      `${percentage.toFixed(1)}%`
    )
  }


  /* ==========================================================
     INTERFAZ
     ========================================================== */

  return (
    <section>

      {/* ======================================================
          HEADER
          ====================================================== */}

      <div className="page-heading row-heading">

        <div>

          <p className="eyebrow">
            Operación en vivo
          </p>

          <h2>
            Control de acceso
          </h2>

          <p>
            Captura rostro y placa para
            validar el acceso mediante
            SmartPark AI.
          </p>

        </div>


        <div className="access-system-state">

          <span className="access-system-dot" />

          Sistema listo

        </div>

      </div>


      {/* ======================================================
          ERROR
          ====================================================== */}

      {error && (

        <div className="alert error">
          {error}
        </div>

      )}


      <div className="access-control-grid">

        {/* ====================================================
            CÁMARA
            ==================================================== */}

        <article className="panel">

          <div className="panel-header">

            <div>

              <h3>
                Cámara de acceso
              </h3>

              <p>
                Captura la evidencia para
                reconocimiento facial y OCR.
              </p>

            </div>

          </div>


          <div className="access-camera-body">

            {/* ================================================
                EVENT TYPE
                ================================================ */}

            <div className="access-event-selector">

              <button
                type="button"
                className={
                  eventType === "ENTRY"
                    ? "access-event-button active"
                    : "access-event-button"
                }
                onClick={
                  () =>
                    setEventType(
                      "ENTRY"
                    )
                }
              >

                <LogIn size={18} />

                Entrada

              </button>


              <button
                type="button"
                className={
                  eventType === "EXIT"
                    ? "access-event-button active"
                    : "access-event-button"
                }
                onClick={
                  () =>
                    setEventType(
                      "EXIT"
                    )
                }
              >

                <LogOut size={18} />

                Salida

              </button>

            </div>


            {/* ================================================
                CAMERA
                ================================================ */}

            <div className="access-camera-zone">

              <video
                ref={videoRef}
                autoPlay
                muted
                playsInline
                className={
                  cameraActive
                    ? "access-camera-video active"
                    : "access-camera-video"
                }
              />


              {!cameraActive && (

                <div className="access-camera-placeholder">

                  <div className="camera-placeholder-icon">

                    <Camera size={36} />

                  </div>

                  <strong>
                    Cámara desactivada
                  </strong>

                  <span>
                    Activa la cámara para
                    capturar rostro y placa.
                  </span>

                </div>

              )}


              {cameraActive && (

                <div className="camera-live-badge">

                  <span />

                  EN VIVO

                </div>

              )}

            </div>


            {cameraError && (

              <div className="camera-error">
                {cameraError}
              </div>

            )}


            {/* ================================================
                CAMERA CONTROLS
                ================================================ */}

            <div className="access-camera-actions">

              {!cameraActive ? (

                <button
                  className="primary-button"
                  type="button"
                  onClick={startCamera}
                >

                  <Camera size={18} />

                  Activar cámara

                </button>

              ) : (

                <button
                  className="secondary-button"
                  type="button"
                  onClick={stopCamera}
                >

                  <CameraOff size={18} />

                  Desactivar cámara

                </button>

              )}


              <button
                className="secondary-button"
                type="button"
                onClick={resetCaptures}
                disabled={
                  !faceCapture
                  &&
                  !plateCapture
                }
              >

                <RotateCcw size={18} />

                Limpiar capturas

              </button>

            </div>


            {/* ================================================
                CAPTURE BUTTONS
                ================================================ */}

            <div className="access-capture-buttons">

              <button
                type="button"
                className={
                  faceCapture
                    ? "access-capture-button complete"
                    : "access-capture-button"
                }
                onClick={
                  () =>
                    captureFrame(
                      "face"
                    )
                }
                disabled={
                  !cameraActive
                }
              >

                {faceCapture ? (
                  <CheckCircle2 size={21} />
                ) : (
                  <ScanFace size={21} />
                )}

                <div>

                  <strong>
                    {faceCapture
                      ? "Rostro capturado"
                      : "Capturar rostro"}
                  </strong>

                  <span>
                    Fotografía del conductor
                  </span>

                </div>

              </button>


              <button
                type="button"
                className={
                  plateCapture
                    ? "access-capture-button complete"
                    : "access-capture-button"
                }
                onClick={
                  () =>
                    captureFrame(
                      "plate"
                    )
                }
                disabled={
                  !cameraActive
                }
              >

                {plateCapture ? (
                  <CheckCircle2 size={21} />
                ) : (
                  <Car size={21} />
                )}

                <div>

                  <strong>
                    {plateCapture
                      ? "Placa capturada"
                      : "Capturar placa"}
                  </strong>

                  <span>
                    Imagen clara de la matrícula
                  </span>

                </div>

              </button>

            </div>


            {/* ================================================
                PREVIEWS
                ================================================ */}

            {(faceCapture || plateCapture) && (

              <div className="access-preview-grid">

                <div className="access-preview-card">

                  <div className="access-preview-title">

                    <ScanFace size={16} />

                    Rostro

                  </div>


                  {faceCapture ? (

                    <img
                      src={
                        faceCapture.preview
                      }
                      alt="Captura del rostro"
                    />

                  ) : (

                    <div className="access-preview-empty">
                      Sin captura
                    </div>

                  )}

                </div>


                <div className="access-preview-card">

                  <div className="access-preview-title">

                    <Car size={16} />

                    Placa

                  </div>


                  {plateCapture ? (

                    <img
                      src={
                        plateCapture.preview
                      }
                      alt="Captura de placa"
                    />

                  ) : (

                    <div className="access-preview-empty">
                      Sin captura
                    </div>

                  )}

                </div>

              </div>

            )}


            {/* ================================================
                PROCESS
                ================================================ */}

            <button
              type="button"
              className="primary-button access-process-button"
              onClick={handleProcess}
              disabled={
                processing
                ||
                !faceCapture
                ||
                !plateCapture
              }
            >

              <ShieldCheck size={20} />

              {processing
                ? "Procesando acceso..."
                : "Procesar acceso"}

            </button>

          </div>

        </article>


        {/* ====================================================
            RESULTADO
            ==================================================== */}

        <div className="access-result-column">

          <article className="panel">

            <div className="panel-header">

              <div>

                <h3>
                  Resultado
                </h3>

                <p>
                  Decisión de SmartPark.
                </p>

              </div>

            </div>


            {!result ? (

              <div className="access-result-empty">

                <div className="access-result-empty-icon">

                  <ShieldCheck size={34} />

                </div>

                <strong>
                  Esperando análisis
                </strong>

                <p>
                  Captura el rostro y la placa
                  para procesar el acceso.
                </p>

              </div>

            ) : (

              <div className="access-result-body">

                {/* ============================================
                    DECISION
                    ============================================ */}

                <div
                  className={
                    authorized
                      ? "access-decision authorized"
                      : denied
                        ? "access-decision denied"
                        : "access-decision unknown"
                  }
                >

                  <div className="access-decision-icon">

                    {authorized ? (

                      <ShieldCheck
                        size={28}
                      />

                    ) : (

                      <ShieldX
                        size={28}
                      />

                    )}

                  </div>


                  <div>

                    <span>
                      Decisión
                    </span>

                    <strong>

                      {authorized
                        ? "ACCESO AUTORIZADO"
                        : denied
                          ? "ACCESO DENEGADO"
                          : decision
                            || "SIN DECISIÓN"}

                    </strong>

                  </div>

                </div>


                {/* ============================================
                    DETAILS
                    ============================================ */}

                <div className="access-result-list">

                  <div className="access-result-item">

                    <span>
                      Movimiento
                    </span>

                    <strong>
                      {result.event_type
                        === "EXIT"
                        ? "SALIDA"
                        : "ENTRADA"}
                    </strong>

                  </div>


                  <div className="access-result-item">

                    <span>
                      Persona
                    </span>

                    <strong>
                      {person}
                    </strong>

                  </div>


                  <div className="access-result-item">

                    <span>
                      Coincidencia facial
                    </span>

                    <strong>
                      {formatScore(
                        result.face_score
                      )}
                    </strong>

                  </div>


                  <div className="access-result-item">

                    <span>
                      Placa detectada
                    </span>

                    <strong className="access-result-plate">
                      {detectedPlate}
                    </strong>

                  </div>


                  <div className="access-result-item">

                    <span>
                      Confianza OCR
                    </span>

                    <strong>
                      {formatScore(
                        result.plate_score
                      )}
                    </strong>

                  </div>


                  <div className="access-result-item">

                    <span>
                      Motivo
                    </span>

                    <strong>
                      {reason}
                    </strong>

                  </div>

                </div>


                {/* ============================================
                    BARRIER
                    ============================================ */}

                <div
                  className={
                    authorized
                      ? "barrier-result open"
                      : "barrier-result closed"
                  }
                >

                  <span>
                    Barrera
                  </span>

                  <strong>

                    {authorized
                      ? "APERTURA SOLICITADA"
                      : "CERRADA"}

                  </strong>

                </div>

              </div>

            )}

          </article>


          <div className="access-flow-card">

            <strong>
              Flujo SmartPark
            </strong>

            <div className="access-flow-step">
              1. Detección facial con ArcFace
            </div>

            <div className="access-flow-step">
              2. Lectura de placa con OCR
            </div>

            <div className="access-flow-step">
              3. Validación de usuario y vehículo
            </div>

            <div className="access-flow-step">
              4. Validación del permiso
            </div>

            <div className="access-flow-step">
              5. Comando a barrera mediante IoT
            </div>

          </div>

        </div>

      </div>

    </section>
  )
}


export default AccessControl