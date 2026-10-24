// Which Civitai picture to save, and where it may come from. No DOM and no
// ComfyUI imports, so tests/preview_pick.test.mjs runs it under node:test.

export const PICTURE_HOST = "image.civitai.com";
export const PICTURE_WIDTH = 450;
export const MAX_PICTURE_BYTES = 8 * 1024 * 1024;

// Civitai rates each picture. The number is a set of flags: 1 = PG,
// 2 = PG-13, 4 = R, 8 = X, 16 = XXX. Older answers give a word instead.
const MILD_LEVEL = 2;
const MILD_WORDS = new Set(["none", "soft"]);

export function isMild(image) {
  const level = Number(image?.nsfwLevel);
  if (Number.isFinite(level) && level > 0) return level <= MILD_LEVEL;
  if (typeof image?.nsfw === "string") return MILD_WORDS.has(image.nsfw.toLowerCase());
  if (image?.nsfw === false) return true;
  return false;
}

// The first still picture in Civitai's answer that may be saved: only mild
// ones unless the person allowed mature pictures.
export function pickPicture(info, allowMature = false) {
  const images = Array.isArray(info?.images) ? info.images : [];
  return images.find((image) =>
    image && typeof image.url === "string"
    && (image.type ?? "image") === "image"
    && (allowMature || isMild(image))
    && smallPictureUrl(image.url) !== null) ?? null;
}

// The address of a small copy of the picture, or null for any address that
// is not Civitai's picture server over https.
export function smallPictureUrl(url) {
  let parsed;
  try {
    parsed = new URL(url);
  } catch {
    return null;
  }
  if (parsed.protocol !== "https:" || parsed.hostname !== PICTURE_HOST) return null;
  const parts = parsed.pathname.split("/");
  const sizing = parts.findIndex((part, index) => index > 1 && index < parts.length - 1 && part.includes("="));
  if (sizing >= 0) parts[sizing] = `width=${PICTURE_WIDTH}`;
  else if (parts.length >= 3) parts.splice(parts.length - 1, 0, `width=${PICTURE_WIDTH}`);
  else return null;
  parsed.pathname = parts.join("/");
  parsed.search = "";
  parsed.hash = "";
  return parsed.href;
}

// Where the picture really came from, after Civitai's redirects: Civitai's
// own servers, over https.
export function isCivitaiAddress(url) {
  try {
    const parsed = new URL(url);
    return parsed.protocol === "https:"
      && (parsed.hostname === "civitai.com" || parsed.hostname.endsWith(".civitai.com"));
  } catch {
    return false;
  }
}
