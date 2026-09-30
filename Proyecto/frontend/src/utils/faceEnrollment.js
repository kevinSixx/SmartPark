export const MIN_FACE_IMAGES = 3
export const MAX_FACE_IMAGES = 5
export const MAX_FACE_FILE_SIZE = 10 * 1024 * 1024
export const FACE_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"]

export async function loadUserFaceState(userId, getUser, getFaceProfile) {
  const user = await getUser(userId)
  try {
    const profile = await getFaceProfile(userId)
    return { user, hasProfile: profile !== null, profileError: null }
  } catch (error) {
    if (error.status === 404) {
      return { user, hasProfile: false, profileError: null }
    }
    return { user, hasProfile: false, profileError: error }
  }
}

export function faceFileSignature(file) {
  return `${file.name}:${file.size}:${file.lastModified}`
}

export function validateFaceFile(file, existingSignatures) {
  if (!FACE_IMAGE_TYPES.includes(file.type)) {
    return `El archivo "${file.name}" no tiene un formato permitido. Usa JPG, PNG o WEBP.`
  }
  if (file.size > MAX_FACE_FILE_SIZE) {
    return `El archivo "${file.name}" supera el límite de 10 MB.`
  }
  if (existingSignatures.has(faceFileSignature(file))) {
    return `La fotografía "${file.name}" ya está seleccionada.`
  }
  return ""
}

export function validateFaceImageCount(count) {
  if (count < MIN_FACE_IMAGES) return `Selecciona o captura al menos ${MIN_FACE_IMAGES} fotografías.`
  if (count > MAX_FACE_IMAGES) return `Solo puedes utilizar hasta ${MAX_FACE_IMAGES} fotografías.`
  return ""
}
