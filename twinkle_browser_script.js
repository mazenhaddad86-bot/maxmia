// ============================================================
// TWINKLE TWINKLE LITTLE STAR — Browser Auto Generator
// Max & Mia World | Nano Banana Pro + Kling 2.5 Turbo
// Paste ONCE in F12 Console on higgsfield.ai tab
// ============================================================

const API = 'https://fnf.higgsfield.ai';
const MAX_CONCURRENT_IMAGES = 1; // one image at a time — Higgsfield queue limit
const MAX_CONCURRENT_VIDEOS = 2; // videos can run 2 parallel

const STORYBOARD = [
  { id:'C01', prompt:'3D animated children\'s scene, girl Mia brown pigtails red ribbon pink star-dress, boy Max curly brown hair blue sweater brown dungarees dinosaur patch red sneakers, standing in garden at dusk, pointing at first star appearing in purple sky, cozy cottage behind them, Pixar style, bright colors' },
  { id:'C02', prompt:'3D animated closeup, girl Mia brown pigtails red ribbon, wide sparkling eyes looking up at night sky with wonder, soft purple twilight glow, Pixar style' },
  { id:'C03', prompt:'3D animated magical night sky, single bright golden star appearing and twinkling above rolling hills, purple-blue gradient sky, soft glowing light, cinematic' },
  { id:'C04', prompt:'3D animated children\'s scene, Max and Mia sitting on cozy blanket in garden at night, looking up at starry sky, fireflies around them, Pixar style' },
  { id:'C05', prompt:'3D animated magical night sky full of twinkling golden stars, milky way visible, deep blue sky, cinematic wide shot' },
  { id:'C06', prompt:'3D animated closeup, girl Mia brown pigtails red ribbon pink dress, singing happily mouth open wide smile, starry night background, Pixar style' },
  { id:'C07', prompt:'3D animated scene, boy Max curly brown hair blue sweater brown dungarees, looking through small toy telescope at night sky, cozy garden setting, stars above, Pixar style' },
  { id:'C08', prompt:'3D animated POV through telescope, giant glowing golden star up close, sparkling and twinkling, magical glow, deep space background' },
  { id:'C09', prompt:'3D animated magical star growing brighter and bigger in night sky, golden rays of light spreading outward, purple-blue sky, cinematic' },
  { id:'C10', prompt:'3D animated cute glowing star character with big round eyes and tiny arms, floating in night sky, golden sparkling light, magical Pixar style' },
  { id:'C11', prompt:'3D animated cute golden star character waving happily at two children below, magical sparkles, night sky background, Pixar style' },
  { id:'C12', prompt:'3D animated Max and Mia waving up excitedly at glowing star, big smiles, garden at night, starry sky above, Pixar style' },
  { id:'C13', prompt:'3D animated cute golden star character gently floating down from sky toward two children, magical sparkle trail, night garden setting' },
  { id:'C14', prompt:'3D animated cute glowing star character landing softly in front of Max and Mia, golden light radiating, children amazed expressions, Pixar style' },
  { id:'C15', prompt:'3D animated girl Mia brown pigtails pink dress, gently reaching out finger to touch glowing star character, magical sparkles at fingertip, wonder expression' },
  { id:'C16', prompt:'3D animated Max, Mia and cute star character dancing together in garden at night, sparkles flying, big smiles, joyful scene, Pixar style' },
  { id:'C17', prompt:'3D animated cute star character pointing up at full starry night sky, Max and Mia looking up with wonder, magical atmosphere' },
  { id:'C18', prompt:'3D animated night sky with star constellations forming cute animal shapes (cat, dog, rabbit) glowing golden, Max and Mia watching below, Pixar style' },
  { id:'C19', prompt:'3D animated bright shooting star streaking across night sky leaving golden trail, magical cinematic shot' },
  { id:'C20', prompt:'3D animated Max and Mia running through garden chasing shooting star, laughing, sparkles around them, night setting, Pixar style' },
  { id:'C21', prompt:'3D animated tiny glowing meteor landing softly in grass, Max and Mia leaning over it curious, golden glow, night garden' },
  { id:'C22', prompt:'3D animated boy Max holding small glowing golden stone in hands, warm golden light on his face, amazed smile, night setting' },
  { id:'C23', prompt:'3D animated girl Mia and cute star character laughing together, star jumping, sparkles everywhere, joyful night scene' },
  { id:'C24', prompt:'3D animated Max, Mia and star character all looking up as large beautiful full moon appears between clouds, silvery glow, magical' },
  { id:'C25', prompt:'3D animated peaceful garden bathed in soft silver moonlight, flowers glowing, fireflies, Max and Mia standing in magical light' },
  { id:'C26', prompt:'3D animated cute star character spreading tiny arms preparing to fly back up, Max and Mia watching sadly, bittersweet expression' },
  { id:'C27', prompt:'3D animated Mia hugging cute glowing star character, Max patting it gently, warm golden glow, emotional sweet scene, Pixar style' },
  { id:'C28', prompt:'3D animated cute star character flying back up into starry night sky, leaving golden sparkle trail, Max and Mia waving goodbye below' },
  { id:'C29', prompt:'3D animated night sky, cute glowing star character high up among other stars waving down, small Max and Mia visible below waving up' },
  { id:'C30', prompt:'3D animated boy Max curly brown hair yawning with sleepy eyes, stars in background, cozy night atmosphere, Pixar style' },
  { id:'C31', prompt:'3D animated girl Mia resting her head on boy Max shoulder, both sleepy, sitting under stars, cozy blanket, peaceful night scene' },
  { id:'C32', prompt:'3D animated warm cottage window glowing, silhouette of mother at door calling children, Max and Mia getting up from blanket' },
  { id:'C33', prompt:'3D animated cozy children\'s bedroom, Max and Mia in beds looking out window at starry sky, moonlight through curtains, stuffed animals' },
  { id:'C34', prompt:'3D animated view through bedroom window, the same cute golden star character twinkling in the night sky, moonlit garden below, peaceful goodnight scene' },
  { id:'C35', prompt:'3D animated wide magical night sky panorama, hundreds of golden stars twinkling over cozy cottage with warm glowing windows, fireflies, peaceful and enchanting, Pixar style' },
  { id:'C36', prompt:'3D animated Max and Mia sleeping peacefully in cozy beds, stuffed animals beside them, moonlight streaming through curtains, golden star glowing outside window, Pixar style' },
];

const VIDEO_PROMPTS = [
  'camera slowly pans up from children toward the first star in the evening sky, gentle breeze',
  'slow zoom into Mia\'s wide sparkling eyes, soft golden light grows',
  'star gently pulses and twinkles, glowing brighter, golden rays spread outward',
  'fireflies drift slowly around children, both look up with peaceful smiles',
  'slow cinematic pan across the full starry sky, stars shimmer softly',
  'Mia\'s head sways as she sings, sparkles float around her',
  'Max slowly adjusts telescope and peers through, gentle movement',
  'star grows larger filling the view, sparkling and pulsing with golden light',
  'star radiates brighter, golden rays spread outward, magical expansion',
  'star character blinks its big eyes and floats gently, sparkles drift',
  'star character waves both tiny arms, sparkles fly with each wave',
  'Max and Mia wave arms excitedly together, big joyful smiles',
  'star descends slowly leaving a glowing sparkle trail behind it',
  'star touches down gently, golden light pulses, children step back in awe',
  'Mia\'s finger slowly reaches toward the star, glow brightens at fingertip',
  'all three spin and dance joyfully, sparkles explode around them',
  'star gestures upward, Max and Mia tilt heads back gazing at sky',
  'star shapes slowly connect forming cute animal outlines one by one',
  'shooting star streaks across the sky, golden trail lingers and fades',
  'Max and Mia sprint through the garden laughing, sparkles trail behind',
  'tiny stone glows softly on the grass, both lean in curiously',
  'warm golden light from stone illuminates Max\'s amazed face',
  'Mia and star laugh together, star jumps up and down gleefully',
  'full moon slowly rises between clouds, silver glow spreads',
  'gentle silver moonlight ripples across flowers, fireflies drift peacefully',
  'star floats slightly upward, Max and Mia reach out sadly',
  'warm glowing hug, star sparkles brighten as Mia embraces it',
  'star rises gracefully into sky, beautiful ascending sparkle trail',
  'star waves from high above, children wave back from far below',
  'Max yawns sleepily, eyes drooping, head nodding gently',
  'Mia gently rests head on Max\'s shoulder, both sigh contentedly',
  'warm cottage door opens, mother waves, children slowly stand up',
  'moonlight streams softly through curtains, children gaze at stars',
  'star twinkles softly, gentle golden pulse, peaceful goodnight glow',
  'slow pan across the magical starry sky over the cozy cottage',
  'gentle breathing, peaceful sleep, moonlight and star glow through window',
];

// === Core state ===
let progress = (() => {
  try {
    const p = JSON.parse(localStorage.getItem('twinkle_progress') || '{"images":{},"videos":{}}');
    // Auto-clean: remove stale entries (jobSetId saved but no url = old failed job)
    let cleaned = 0;
    Object.keys(p.images).forEach(k => { if (p.images[k].jobSetId && !p.images[k].url) { delete p.images[k]; cleaned++; }});
    Object.keys(p.videos).forEach(k => { if (p.videos[k].jobSetId && !p.videos[k].url) { delete p.videos[k]; cleaned++; }});
    if (cleaned > 0) { localStorage.setItem('twinkle_progress', JSON.stringify(p)); console.log(`%c🧹 Auto-cleaned ${cleaned} stale jobs`, 'color:orange'); }
    return p;
  }
  catch(e) { return {images:{}, videos:{}}; }
})();

let _token = null;
let _tokenTs = 0;

async function getToken() {
  const now = Date.now() / 1000;
  if (_token && now < _tokenTs + 240) return _token; // reuse if <4min old
  try { await window.Clerk.session.touch(); } catch(e) {}
  const t = await window.Clerk.session.getToken();
  if (!t) throw new Error('Token null — Clerk session broken');
  _token = t; _tokenTs = now;
  console.log('%c🔑 Token refreshed', 'color:gray');
  return t;
}

async function api(method, path, body) {
  const t = await getToken();
  const r = await fetch(API + path, {
    method,
    headers: {'Authorization':'Bearer '+t, 'Content-Type':'application/json'},
    body: body ? JSON.stringify(body) : undefined
  });
  const text = await r.text();
  if (!r.ok) throw new Error(`${method} ${path} → ${r.status}: ${text.slice(0,200)}`);
  return JSON.parse(text);
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

function saveProgress() {
  localStorage.setItem('twinkle_progress', JSON.stringify(progress));
}

async function waitForJob(jobSetId, label) {
  for (let i = 0; i < 180; i++) { // max 15 min
    await sleep(5000);
    let found = null;
    try {
      // Try direct endpoint first
      const d = await api('GET', '/jobs/' + jobSetId);
      const status = d.status || d.job_set_status || d.jobs?.[0]?.status;
      const result = d.result || d.jobs?.[0]?.result || d.job_sets?.[0]?.jobs?.[0]?.result;
      if (status === 'completed' || status === 'done' || result?.url) return result || d;
      if (status === 'failed' || status === 'error') throw new Error(`Job failed: ${jobSetId}`);
      if (i % 12 === 0) console.log(`  ⏳ ${label} [direct] [${status}] ${i*5}s`);
      continue;
    } catch(e) {
      if (!e.message.includes('404')) { if (i % 12 === 0) console.log(`  ⏳ ${label} retry... ${i*5}s`); continue; }
      // 404 → fallback: search in jobs list
    }
    try {
      const list = await api('GET', '/jobs?page=1&per_page=50');
      const jobs = list.jobs || list.job_sets || [];
      found = jobs.find(j =>
        j.job_set_id === jobSetId || j.id === jobSetId ||
        j.jobs?.some(jj => jj.job_set_id === jobSetId)
      );
    } catch(e2) { continue; }

    if (!found) { if (i % 12 === 0) console.log(`  ⏳ ${label} [list-search] not found yet ${i*5}s`); continue; }

    const status = found.status || found.job_set_status || found.jobs?.[0]?.status;
    const result = found.result || found.jobs?.[0]?.result;
    if (i % 6 === 0) console.log(`  ⏳ ${label} [list] [${status}] ${i*5}s`);
    if (status === 'completed' || status === 'done' || result?.url) return result || found;
    if (status === 'failed' || status === 'error') throw new Error(`Job failed: ${jobSetId}`);
  }
  throw new Error(`Timeout after 15min: ${jobSetId}`);
}

const REF_IMG = {
  id: '72f08f7b-7ca0-4301-bc35-922144447c47',
  url: 'https://d2ol7oe51mr4n9.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/72f08f7b-7ca0-4301-bc35-922144447c47.png',
  type: 'media_input'
};

function extractUrl(obj) {
  if (!obj) return null;
  return obj.url || obj.output_url || obj.image_url ||
    obj.result?.url || obj.jobs?.[0]?.result?.url ||
    obj.job_sets?.[0]?.jobs?.[0]?.result?.url ||
    obj.output?.[0] || obj.results?.[0]?.url || null;
}

function extractId(obj) {
  if (!obj) return null;
  return obj.id || obj.uuid || obj.image_id || obj.media_id ||
    obj.jobs?.[0]?.id || obj.job_sets?.[0]?.jobs?.[0]?.id || null;
}

async function pollImageJob(jobSetId, label) {
  // Image jobs: try multiple endpoints since /jobs/{id} gives 404
  const endpoints = [
    '/jobs/' + jobSetId,
    '/job-sets/' + jobSetId,
    '/image-jobs/' + jobSetId,
    '/generations/' + jobSetId,
  ];
  for (let i = 0; i < 180; i++) {
    await sleep(5000);
    // Try all known endpoints
    for (const ep of endpoints) {
      try {
        const d = await api('GET', ep);
        const url = extractUrl(d);
        if (url) { console.log(`%c✅ ${label} found via ${ep}`, 'color:green'); return d; }
        const status = d.status || d.job_set_status || d.jobs?.[0]?.status;
        if (status === 'failed' || status === 'error') throw new Error(`Job failed: ${jobSetId}`);
        if (status && i % 12 === 0) console.log(`  ⏳ ${label} [${ep.split('/')[1]}] [${status}] ${i*5}s`);
        break; // found a working endpoint, stop trying others
      } catch(e) {
        if (!e.message.includes('404') && !e.message.includes('405')) throw e;
      }
    }
    // Also search in jobs list (video-style)
    try {
      const list = await api('GET', '/jobs?page=1&per_page=50');
      const jobs = list.jobs || list.job_sets || [];
      const found = jobs.find(j => j.job_set_id === jobSetId || j.id === jobSetId);
      if (found) {
        const url = extractUrl(found);
        if (url) return found;
        const status = found.status || found.job_set_status;
        if (i % 6 === 0) console.log(`  ⏳ ${label} [list] [${status}] ${i*5}s`);
      }
    } catch(e2) {}
    if (i % 12 === 0) console.log(`  ⏳ ${label} waiting ${i*5}s...`);
  }
  throw new Error(`Timeout: ${jobSetId}`);
}

async function generateImage(clip) {
  // Already fully done
  if (progress.images[clip.id]?.url) {
    console.log(`%c✅ ${clip.id} image cached`, 'color:green');
    return progress.images[clip.id];
  }

  // Submit new job (stale jobSetIds are auto-cleaned at startup)
  const submitTime = Date.now();
  const d = await api('POST', '/jobs/nano-banana-2', {
    use_unlim: true,
    params: {
      width: 1376, height: 768,
      aspect_ratio: '16:9',
      resolution: '1k',
      batch_size: 1,
      prompt: clip.prompt,
      input_images: [REF_IMG],
    }
  });

  console.log(`%c🔍 ${clip.id} POST response:`, 'color:gray', JSON.stringify(d).slice(0, 400));

  const cost = d.job_sets?.[0]?.cost ?? d.cost ?? null;
  if (cost !== null && cost !== undefined && cost > 0) throw new Error(`💸 COST DETECTED ${cost} credits! ABORTING!`);

  // Check if result is already in the POST response (some APIs return synchronously)
  const directUrl = extractUrl(d);
  if (directUrl) {
    const imgId = extractId(d) || clip.id;
    const data = { id: imgId, url: directUrl, jobSetId: imgId };
    progress.images[clip.id] = data;
    saveProgress();
    console.log(`%c✅ ${clip.id} image done (sync response!)`, 'color:green');
    return data;
  }

  // Extract jobSetId for polling
  const jobSetId = d.job_sets?.[0]?.id || d.job_set_id || d.jobs?.[0]?.job_set_id;
  if (!jobSetId) throw new Error(`No jobSetId: ${JSON.stringify(d).slice(0,200)}`);

  progress.images[clip.id] = { jobSetId };
  saveProgress();
  console.log(`%c🖼️ ${clip.id} submitted [${jobSetId.slice(0,8)}] cost:${cost}`, 'color:#4af');

  const result = await pollImageJob(jobSetId, clip.id);
  const url = extractUrl(result);
  const imgId = extractId(result) || jobSetId;

  if (!url) throw new Error(`No URL for ${clip.id}: ${JSON.stringify(result).slice(0,200)}`);

  const data = { id: imgId, url, jobSetId };
  progress.images[clip.id] = data;
  saveProgress();
  console.log(`%c✅ ${clip.id} image done: ${url.slice(-50)}`, 'color:green');
  return data;
}

async function generateVideo(clip, imgData, videoPrompt) {
  // Already done
  if (progress.videos[clip.id]?.url) {
    console.log(`%c✅ ${clip.id} video cached`, 'color:green');
    return progress.videos[clip.id];
  }

  // Already submitted before F5 — resume polling
  if (progress.videos[clip.id]?.jobSetId) {
    const existingId = progress.videos[clip.id].jobSetId;
    console.log(`%c⏳ ${clip.id} resuming video job ${existingId.slice(0,8)}`, 'color:orange');
    const result = await waitForJob(existingId, clip.id);
    const url = result.url || result.output?.[0];
    if (!url) throw new Error(`No video URL resuming ${clip.id}`);
    const data = { url, jobSetId: existingId };
    progress.videos[clip.id] = data;
    saveProgress();
    console.log(`%c✅ ${clip.id} video done (resumed)`, 'color:green');
    return data;
  }

  const d = await api('POST', '/jobs/kling', {
    params: {
      model: 'kling-v2-5-turbo',
      prompt: videoPrompt,
      duration: 5,
      enhance_prompt: true,
      mode: 'std',
      width: 1376, height: 768,
      use_unlim: true,
      input_image: { id: imgData.id, url: imgData.url, type: 'image_job' },
      negative_prompt: 'transitions, scene cuts, fading, cross fade, bad quality, low quality',
      motion_id: '7077cde8-7947-46d6-aea2-dbf2ff9d441c'
    }
  });

  const cost = d.job_sets?.[0]?.cost ?? d.cost;
  if (cost > 0) throw new Error(`💸 COST DETECTED ${cost} credits! ABORTING!`);

  const jobSetId = d.job_sets?.[0]?.id || d.job_set_id;

  // ✅ Save jobSetId IMMEDIATELY so F5 resume works
  progress.videos[clip.id] = { jobSetId };
  saveProgress();

  console.log(`%c🎬 ${clip.id} video submitted [${jobSetId?.slice(0,8)}] cost:${cost}`, 'color:#a4f');

  const result = await waitForJob(jobSetId, clip.id);
  const url = result.url || result.output?.[0];

  if (!url) throw new Error(`No video URL for ${clip.id}: ${JSON.stringify(result).slice(0,200)}`);

  const data = { url, jobSetId };
  progress.videos[clip.id] = data;
  saveProgress();
  console.log(`%c✅ ${clip.id} video done: ...${url.slice(-30)}`, 'color:green');
  return data;
}

async function runBatch(items, fn, n = MAX_CONCURRENT) {
  const results = new Array(items.length);
  for (let i = 0; i < items.length; i += n) {
    const batch = items.slice(i, i + n);
    const batchNum = Math.floor(i/n) + 1;
    const total = Math.ceil(items.length/n);
    console.log(`\n%c📦 Batch ${batchNum}/${total} (${batch.map(x=>x.id||x.clip?.id).join(', ')})`, 'color:orange;font-weight:bold');
    // allSettled: one failure does NOT kill the whole batch
    const settled = await Promise.allSettled(batch.map((item, j) => fn(item, i+j)));
    for (let j = 0; j < settled.length; j++) {
      if (settled[j].status === 'fulfilled') {
        results[i+j] = settled[j].value;
      } else {
        console.error(`%c❌ ${batch[j]?.id || batch[j]?.clip?.id} FAILED: ${settled[j].reason?.message}`, 'color:red');
        results[i+j] = null; // mark as failed, will be retried on resume
      }
    }
    // 30s pause between batches to avoid Higgsfield rate limiting
    if (i + n < items.length) await sleep(30000);
  }
  return results;
}

// Check active jobs count before starting
async function checkActiveJobs() {
  const d = await api('GET', '/jobs?page=1&per_page=20');
  const active = (d.jobs || []).filter(j => j.status === 'processing' || j.status === 'pending' || j.status === 'queued').length;
  console.log(`Active jobs: ${active}`);
  return active;
}

async function run() {
  console.log('%c🌟 TWINKLE TWINKLE LITTLE STAR — START', 'font-size:16px;color:gold;font-weight:bold');
  console.log(`Images done: ${Object.keys(progress.images).length}/36`);
  console.log(`Videos done: ${Object.keys(progress.videos).length}/36`);

  const active = await checkActiveJobs();
  if (active > 2) {
    console.log(`%c⚠️ ${active} active jobs — waiting 30s...`, 'color:orange');
    await sleep(30000);
  }

  // Phase 1: Images
  console.log('\n%c=== PHASE 1: IMAGES (Nano Banana Pro 16:9) ===', 'color:cyan;font-weight:bold');
  const imageResults = await runBatch(STORYBOARD, async (clip) => generateImage(clip), MAX_CONCURRENT_IMAGES);

  const imgDone = imageResults.filter(Boolean).length;
  console.log(`%c\n✅ IMAGES PHASE DONE: ${imgDone}/36 erfolgreich`, 'color:green;font-size:14px;font-weight:bold');
  if (imgDone < 36) console.log(`%c⚠️ ${36-imgDone} Bilder fehlgeschlagen — werden bei nächstem Resume nachgeholt`, 'color:orange');

  // Phase 2: Videos
  console.log('\n%c=== PHASE 2: VIDEOS (Kling 2.5 Turbo) ===', 'color:magenta;font-weight:bold');
  await runBatch(
    STORYBOARD.map((clip, i) => ({ clip, img: imageResults[i], vp: VIDEO_PROMPTS[i], id: clip.id })).filter(x => x.img),
    async ({ clip, img, vp }) => generateVideo(clip, img, vp),
    MAX_CONCURRENT_VIDEOS
  );

  console.log('%c\n🎉🎉🎉 ALLE 36 VIDEOS FERTIG! 🎉🎉🎉', 'color:gold;font-size:16px;font-weight:bold');
  console.log('Results saved to localStorage key: twinkle_progress');
  console.log('To get results: copy(localStorage.getItem("twinkle_progress"))');
}

// Start!
window._twinkleRun2 = run;
run().catch(e => {
  console.error('%c❌ ERROR:', 'color:red', e.message);
  console.log('%cProgress saved. Run window._twinkleRun2() to resume.', 'color:orange');
});
