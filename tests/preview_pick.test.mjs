import assert from "node:assert/strict";
import test from "node:test";

import { isCivitaiAddress, isMild, pickPicture, smallPictureUrl } from "../web/preview_pick.mjs";

const url = (name) => `https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/0b1c2d3e/width=1024/${name}.jpeg`;

test("only mild pictures are picked unless mature ones are allowed", () => {
  const info = { images: [
    { url: url("video"), type: "video", nsfwLevel: 1 },
    { url: url("r"), type: "image", nsfwLevel: 4 },
    { url: url("pg13"), type: "image", nsfwLevel: 2 },
  ] };
  assert.equal(pickPicture(info).url, url("pg13"));
  assert.equal(pickPicture(info, true).url, url("r"));
  assert.equal(pickPicture({ images: [{ url: url("x"), nsfwLevel: 8 }] }), null);
  assert.equal(pickPicture({}), null);
  assert.equal(pickPicture(null), null);
});

test("older answers rate pictures with a word, and an unrated picture is not mild", () => {
  assert.equal(isMild({ nsfw: "None" }), true);
  assert.equal(isMild({ nsfw: "Soft" }), true);
  assert.equal(isMild({ nsfw: "Mature" }), false);
  assert.equal(isMild({}), false);
});

test("the small copy comes only from Civitai's picture server over https", () => {
  assert.equal(smallPictureUrl(url("a")), "https://image.civitai.com/xG1nkqKTMzGDvpLrqFT7WA/0b1c2d3e/width=450/a.jpeg");
  assert.equal(smallPictureUrl("https://image.civitai.com/key/uuid/original=true/a.png"),
    "https://image.civitai.com/key/uuid/width=450/a.png");
  assert.equal(smallPictureUrl("https://image.civitai.com/key/uuid/a.png"), "https://image.civitai.com/key/uuid/width=450/a.png");
  assert.equal(smallPictureUrl("http://image.civitai.com/key/uuid/width=1024/a.png"), null);
  assert.equal(smallPictureUrl("https://image.civitai.com.example.org/key/uuid/a.png"), null);
  assert.equal(smallPictureUrl("https://example.org/a.png"), null);
  assert.equal(smallPictureUrl("not a url"), null);
  assert.equal(pickPicture({ images: [{ url: "https://example.org/a.png", nsfwLevel: 1 }] }), null);
});

test("after redirects the picture must still be on a Civitai server", () => {
  assert.equal(isCivitaiAddress("https://blobs-b2.civitai.com/file.jpeg"), true);
  assert.equal(isCivitaiAddress("https://civitai.com/file.jpeg"), true);
  assert.equal(isCivitaiAddress("http://blobs-b2.civitai.com/file.jpeg"), false);
  assert.equal(isCivitaiAddress("https://evilcivitai.com/file.jpeg"), false);
  assert.equal(isCivitaiAddress(""), false);
});
