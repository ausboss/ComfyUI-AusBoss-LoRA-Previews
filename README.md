# LoRA Previews for AusBoss LoRA Loader

Shows each LoRA's picture from Civitai when you hover it in
[LoRA Loader 🆎](https://github.com/ausboss/ComfyUI-AusBoss#lora-loader).

Click **Fetch Civitai info** on a LoRA, as you already do for its trigger
words, and this add-on also saves the LoRA's preview picture next to the LoRA
file. From then on, hovering the LoRA's name shows the picture, in the stack
and in the **+ LoRA** list. It adds no nodes and nothing to your workflows.

You need [ComfyUI-AusBoss](https://github.com/ausboss/ComfyUI-AusBoss) 2.19.0
or newer.

## Install

Close ComfyUI first. Nothing extra needs to be installed with pip: the add-on
only uses what ComfyUI already has.

### Windows (portable ComfyUI)

1. Open the folder `ComfyUI_windows_portable\ComfyUI\custom_nodes`.
2. **With Git:** click the folder's address bar, type `cmd` and press Enter.
   In the window that opens, run:

   ```bat
   git clone https://github.com/ausboss/ComfyUI-AusBoss-LoRA-Previews
   ```

   **Without Git:** on this page, click **Code**, then **Download ZIP**.
   Extract the ZIP into `custom_nodes`, so the folder
   `ComfyUI-AusBoss-LoRA-Previews-main` sits there next to your other custom
   nodes.
3. Start ComfyUI.

### macOS and Linux

In a terminal:

```bash
cd /path/to/ComfyUI/custom_nodes
git clone https://github.com/ausboss/ComfyUI-AusBoss-LoRA-Previews
```

Then start ComfyUI. On a Mac without Git, the first `git` command offers to
install Apple's command line tools; you can also use **Code** → **Download
ZIP** and extract it into `custom_nodes` instead.

### ComfyUI Desktop app

The add-on goes in the `custom_nodes` folder of the folder the app runs from.
To find it, open **Settings** → **About**: the folder is listed after
`--base-directory`. Then follow the steps for Windows or macOS above, in that
`custom_nodes` folder, and restart the app.

### Check that it works

1. In LoRA Loader 🆎, click the **i** at the end of a LoRA row.
2. Click **Fetch Civitai info** (or **Refresh Civitai info** if you fetched it
   before).
3. A message says **Saved the preview picture from Civitai**, the picture
   appears in the card, and hovering the LoRA's name shows it.

Files Civitai doesn't know, such as LoRAs you trained yourself, get no
picture.

If the button always reads **Civitai lookup failed**, check whether ComfyUI
was started with `--disable-api-nodes`. That setting stops the browser from
reaching any other site, Civitai included.

## Which picture it saves

The first still picture on the LoRA's Civitai page that Civitai rates PG or
PG-13. To allow any rating, turn on **Allow mature preview pictures** in
ComfyUI's settings, under **🆎 AusBoss** → **LoRA Previews**.

The picture is saved as `<lora name>.preview.jpg` next to the LoRA file, at
most 768 pixels on its longest side and without metadata. If a LoRA already
has a preview picture (any `.preview.png`, `.preview.jpg`, `.png`, `.jpg` or
`.webp` with the LoRA's name), the add-on leaves it alone and saves nothing.

## Update and uninstall

- **Update:** run `git pull` in the `ComfyUI-AusBoss-LoRA-Previews` folder, or
  download the ZIP again and replace the folder. Restart ComfyUI.
- **Uninstall:** delete the folder and restart ComfyUI. Pictures it saved stay
  next to your LoRAs; delete the `.preview.jpg` files if you don't want them.

## Privacy and safety

- Nothing happens until you click **Fetch Civitai info** or **Refresh Civitai
  info**. Then your browser downloads one picture, a 450-pixel-wide copy, from
  Civitai's picture server (`image.civitai.com`), without sending cookies. It
  accepts the picture only if it comes from a Civitai address over https.
- The ComfyUI server part never connects to anything. It takes the picture
  from your browser, checks that it is a picture of a sane size, and writes
  it next to a LoRA that ComfyUI lists in its LoRA folders. It never writes
  anywhere else and never replaces a file.
- The AusBoss pack itself downloads no pictures. That is why this is a
  separate add-on: you choose whether you want it.

## Technical details

- The LoRA Loader sends a browser event, `ausboss:lora-civitai-saved`, with the
  LoRA's name and Civitai's answer after it saves the `.civitai.info` file. The
  add-on answers with `ausboss:lora-preview-saved`, and the LoRA Loader then
  shows the new picture without a reload.
- Server routes: `GET /ausboss_previews/has?name=<lora>` and
  `POST /ausboss_previews/save?name=<lora>` with the picture as the body
  (8 MB at most, 40 megapixels at most).
- Tests: `python tests/test_previews.py` (needs Pillow) and
  `node --test tests/`.

## License

MIT. See [LICENSE](LICENSE).
