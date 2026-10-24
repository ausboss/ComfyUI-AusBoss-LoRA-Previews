// LoRA Previews: when the AusBoss LoRA Loader saves a LoRA's Civitai info,
// download the LoRA's preview picture from Civitai and save it next to the
// LoRA file. Nothing happens until you click Fetch Civitai info.
import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";
import { MAX_PICTURE_BYTES, isCivitaiAddress, pickPicture, smallPictureUrl } from "./preview_pick.mjs";

const VERSION = "1.0.0";
const MATURE_SETTING = "AusBoss.LoRAPreviews.AllowMature";

// The LoRA Loader reads this to know the add-on is installed.
window.ausbossLoraPreviews = { version: VERSION };

function toast(severity, detail) {
  app.extensionManager?.toast?.add?.({ severity, summary: "LoRA Previews", detail, life: 5000 });
}

function allowMature() {
  try {
    return app.extensionManager?.setting?.get?.(MATURE_SETTING) === true;
  } catch {
    return false;
  }
}

async function serverJson(response) {
  try {
    return await response.json();
  } catch {
    return { ok: false, error: `The server answered ${response.status}.` };
  }
}

async function savePreview(name, info) {
  const has = await serverJson(await api.fetchApi(`/ausboss_previews/has?name=${encodeURIComponent(name)}`));
  if (!has.ok) throw new Error(has.error || "Could not check this LoRA.");
  if (has.has) return;
  const picture = pickPicture(info, allowMature());
  if (!picture) {
    toast("info", "Civitai has no picture for this LoRA that can be saved.");
    return;
  }
  const response = await fetch(smallPictureUrl(picture.url), {
    credentials: "omit", referrerPolicy: "no-referrer", cache: "no-store",
  });
  if (!response.ok) throw new Error(`Civitai's picture server answered ${response.status}.`);
  if (!isCivitaiAddress(response.url)) throw new Error("The picture came from somewhere other than Civitai.");
  if (!(response.headers.get("content-type") || "").startsWith("image/")) throw new Error("Civitai did not send a picture.");
  if (Number(response.headers.get("content-length") || 0) > MAX_PICTURE_BYTES) throw new Error("The picture is too large.");
  const blob = await response.blob();
  if (blob.size > MAX_PICTURE_BYTES) throw new Error("The picture is too large.");
  const saved = await serverJson(await api.fetchApi(`/ausboss_previews/save?name=${encodeURIComponent(name)}`, {
    method: "POST",
    headers: { "Content-Type": blob.type || "application/octet-stream" },
    body: blob,
  }));
  if (!saved.ok) throw new Error(saved.error || "Could not save the preview picture.");
  window.dispatchEvent(new CustomEvent("ausboss:lora-preview-saved", { detail: { name } }));
  toast("success", "Saved the preview picture from Civitai.");
}

window.addEventListener("ausboss:lora-civitai-saved", (event) => {
  const { name, info } = event.detail ?? {};
  if (typeof name !== "string" || !name) return;
  savePreview(name, info).catch((error) => toast("warn", String(error?.message || error)));
});

app.registerExtension({
  name: "AusBoss.LoRAPreviews",
  settings: [
    {
      id: MATURE_SETTING,
      name: "Allow mature preview pictures",
      category: ["🆎 AusBoss", "LoRA Previews", "Mature pictures"],
      type: "boolean",
      defaultValue: false,
      tooltip: "Off: only pictures Civitai rates PG or PG-13 are saved. On: the LoRA's first picture, whatever its rating.",
    },
  ],
});
