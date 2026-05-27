// ============================================================
// TWINKLE TWINKLE LITTLE STAR — Browser Auto Generator v2
// 34 Clips | Nano Banana Pro + Kling 2.5 Turbo
// Paste ONCE in F12 Console on higgsfield.ai tab
// ============================================================

const API = 'https://fnf.higgsfield.ai';
const MAX_IMG = 1;  // one image at a time
const MAX_VID = 2;  // 2 videos parallel

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
];

const VIDEO_PROMPTS = [
  'camera slowly pans up from children toward the first star in the purple evening sky, gentle breeze in hair',
  'slow zoom into Mia\'s wide sparkling eyes, soft golden light grows in her gaze',
  'star gently pulses and twinkles, glowing brighter, radiating soft golden light outward',
  'gentle sway, fireflies drift slowly around children, both look up with peaceful smiles',
  'slow cinematic pan across the full starry night sky, stars shimmer and twinkle softly',
  'Mia\'s head sways gently as she sings, sparkles float around her',
  'Max slowly adjusts telescope and peers through, gentle movement, stars twinkling above',
  'star slowly grows larger filling the telescope view, sparkling and pulsing with golden light',
  'star radiates brighter and brighter, golden rays spread outward, magical expansion',
  'cute star character blinks its big eyes and floats gently, sparkles drift around it',
  'star character waves both tiny arms happily, sparkles fly outward with each wave',
  'Max and Mia wave arms excitedly together, big smiles, joyful movement',
  'star descends slowly and gracefully leaving a glowing sparkle trail behind it',
  'star character touches down gently, golden light pulses outward, children step back in awe',
  'Mia\'s finger slowly reaches toward the star, magical golden glow brightens at her fingertip',
  'all three spin and dance joyfully, sparkles explode around them, laughter fills the scene',
  'star gestures upward enthusiastically, Max and Mia tilt heads back gazing at the sky',
  'star shapes slowly connect and glow forming cute animal outlines one by one',
  'shooting star streaks dramatically across the sky, golden trail lingers and fades',
  'Max and Mia sprint through the garden laughing, motion blur, sparkles trail behind them',
  'tiny stone glows softly on the grass, Max and Mia lean in curiously together',
  'warm golden light radiates from stone in Max\'s hands, illuminating his amazed face',
  'Mia and star character laugh together, star jumps up and down gleefully',
  'full moon slowly rises between parting clouds, silvery glow spreads across the garden',
  'gentle silver moonlight ripples across flowers and grass, fireflies drift peacefully',
  'star floats slightly upward, Max and Mia reach out with sad gentle expressions',
  'warm glowing hug, star sparkles brighten as Mia embraces it, Max pats it softly',
  'star rises gracefully into the night sky, leaving a beautiful ascending sparkle trail',
  'star waves from high above among the other stars, children wave back from far below',
  'Max yawns sleepily, eyes drooping, head nodding, stars soft in background',
  'Mia gently rests her head on Max\'s shoulder, both sigh contentedly under the stars',
  'warm cottage door opens, silhouette of mother waves, children slowly stand up',
  'moonlight streams softly through curtains, children gaze peacefully out at the stars',
  'star twinkles softly and lovingly, gentle golden pulse, peaceful goodnight glow',
];

// === State (localStorage key: stars_progress) ===
let P = (() => {
  try { return JSON.parse(localStorage.getItem('stars_progress') || '{"images":{},"videos":{}}'); }
  catch(e) { return {images:{}, videos:{}}; }
})();

let _tok = null, _tokTs = 0;

async function getToken() {
  const now = Date.now() / 1000;
  if (_tok && now < _tokTs + 240) return _tok;
  try { await window.Clerk.session.touch(); } catch(e) {}
  const t = await window.Clerk.session.getToken();
  if (!t) throw new Error('Token null');
  _tok = t; _tokTs = now;
  console.log('%c🔑 Token OK', 'color:gray');
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

const sleep = ms => new Promise(r => setTimeout(r, ms));
const save = () => localStorage.setItem('stars_progress', JSON.stringify(P));

async function waitFor(jobSetId, label) {
  for (let i = 0; i < 180; i++) {
    await sleep(5000);
    let d;
    try { d = await api('GET', '/jobs/' + jobSetId); } catch(e) { continue; }
    const status = d.status || d.job_set_status || d.jobs?.[0]?.status;
    const result = d.result || d.jobs?.[0]?.result || d.job_sets?.[0]?.jobs?.[0]?.result;
    if (status === 'completed' || status === 'done' || result?.url) return result || d;
    if (status === 'failed' || status === 'error') throw new Error(`Job failed: ${jobSetId}`);
    if (i % 12 === 0) console.log(`  ⏳ ${label} [${status}] ${i*5}s`);
  }
  throw new Error(`Timeout: ${jobSetId}`);
}

const REF_IMG = {
  id: '58d881d4-96c8-4051-9a12-6e0e7d11e8ef',
  url: 'https://d2ol7oe51mr4n9.cloudfront.net/user_370wAgHeE16XE3iiqsvYu1TOMBv/58d881d4-96c8-4051-9a12-6e0e7d11e8ef.png',
  type: 'media_input'
};

async function genImage(clip) {
  if (P.images[clip.id]?.url) { console.log(`%c✅ ${clip.id} img cached`, 'color:green'); return P.images[clip.id]; }
  if (P.images[clip.id]?.jobSetId) {
    const id = P.images[clip.id].jobSetId;
    console.log(`%c⏳ ${clip.id} resuming img ${id.slice(0,8)}`, 'color:orange');
    const r = await waitFor(id, clip.id);
    const url = r.url || r.output?.[0];
    if (!url) throw new Error(`No URL resuming ${clip.id}`);
    P.images[clip.id] = { id: r.id||r.uuid||id, url, jobSetId: id }; save();
    return P.images[clip.id];
  }
  const d = await api('POST', '/jobs/nano-banana-2', {
    use_unlim: true,
    params: { width:1376, height:768, aspect_ratio:'16:9', resolution:'1k', batch_size:1, prompt:clip.prompt, input_images:[REF_IMG] }
  });
  console.log(`%c🔍 ${clip.id}:`, 'color:gray', JSON.stringify(d).slice(0,300));
  const cost = d.job_sets?.[0]?.cost ?? d.cost;
  if (cost !== null && cost !== undefined && cost > 0) throw new Error(`💸 COST ${cost}! STOP!`);
  const jobSetId = d.job_set_id || d.job_sets?.[0]?.job_set_id || d.id || d.jobs?.[0]?.job_set_id;
  if (!jobSetId) throw new Error(`No jobSetId for ${clip.id}`);
  P.images[clip.id] = { jobSetId }; save();
  console.log(`%c🖼️ ${clip.id} submitted [${jobSetId.slice(0,8)}] cost:${cost}`, 'color:#4af');
  const r = await waitFor(jobSetId, clip.id);
  const url = r.url || r.output?.[0];
  if (!url) throw new Error(`No URL for ${clip.id}`);
  P.images[clip.id] = { id: r.id||r.uuid||jobSetId, url, jobSetId }; save();
  console.log(`%c✅ ${clip.id} img done`, 'color:green');
  return P.images[clip.id];
}

async function genVideo(clip, img, vp) {
  if (P.videos[clip.id]?.url) { console.log(`%c✅ ${clip.id} vid cached`, 'color:green'); return P.videos[clip.id]; }
  if (P.videos[clip.id]?.jobSetId) {
    const id = P.videos[clip.id].jobSetId;
    console.log(`%c⏳ ${clip.id} resuming vid ${id.slice(0,8)}`, 'color:orange');
    const r = await waitFor(id, clip.id);
    const url = r.url || r.output?.[0];
    if (!url) throw new Error(`No vid URL resuming ${clip.id}`);
    P.videos[clip.id] = { url, jobSetId: id }; save();
    return P.videos[clip.id];
  }
  const d = await api('POST', '/jobs/kling', {
    params: { model:'kling-v2-5-turbo', prompt:vp, duration:5, enhance_prompt:true, mode:'std',
      width:1376, height:768, use_unlim:true,
      input_image: { id:img.id, url:img.url, type:'image_job' },
      negative_prompt:'transitions, scene cuts, fading, cross fade, bad quality, low quality',
      motion_id:'7077cde8-7947-46d6-aea2-dbf2ff9d441c' }
  });
  const cost = d.job_sets?.[0]?.cost ?? d.cost;
  if (cost > 0) throw new Error(`💸 COST ${cost}! STOP!`);
  const jobSetId = d.job_sets?.[0]?.job_set_id || d.job_set_id;
  P.videos[clip.id] = { jobSetId }; save();
  console.log(`%c🎬 ${clip.id} vid submitted [${jobSetId?.slice(0,8)}] cost:${cost}`, 'color:#a4f');
  const r = await waitFor(jobSetId, clip.id);
  const url = r.url || r.output?.[0];
  if (!url) throw new Error(`No vid URL for ${clip.id}`);
  P.videos[clip.id] = { url, jobSetId }; save();
  console.log(`%c✅ ${clip.id} vid done`, 'color:green');
  return P.videos[clip.id];
}

async function runBatch(items, fn, n) {
  const results = [];
  for (let i = 0; i < items.length; i += n) {
    const batch = items.slice(i, i+n);
    console.log(`\n%c📦 Batch ${Math.floor(i/n)+1}/${Math.ceil(items.length/n)} (${batch.map(x=>x.id||x.clip?.id).join(', ')})`, 'color:orange;font-weight:bold');
    const settled = await Promise.allSettled(batch.map(item => fn(item)));
    for (const [j, s] of settled.entries()) {
      if (s.status === 'fulfilled') results.push(s.value);
      else { console.error(`%c❌ ${batch[j]?.id||batch[j]?.clip?.id}: ${s.reason?.message}`, 'color:red'); results.push(null); }
    }
    if (i+n < items.length) await sleep(2000);
  }
  return results;
}

async function run() {
  console.log('%c🌟 STARS VIDEO v2 — START (34 Clips)', 'font-size:16px;color:gold;font-weight:bold');
  console.log(`Images: ${Object.keys(P.images).length}/34 | Videos: ${Object.keys(P.videos).length}/34`);

  const jobs = await api('GET', '/jobs?page=1&per_page=20');
  const active = (jobs.jobs||[]).filter(j => ['processing','pending','queued'].includes(j.status)).length;
  if (active > 2) { console.log(`%c⚠️ ${active} active — waiting 30s`, 'color:orange'); await sleep(30000); }

  // Phase 1: Images
  console.log('\n%c=== PHASE 1: IMAGES ===', 'color:cyan;font-weight:bold');
  const imgs = await runBatch(STORYBOARD, clip => genImage(clip), MAX_IMG);
  console.log(`%c✅ Images: ${imgs.filter(Boolean).length}/34`, 'color:green;font-weight:bold');

  // Phase 2: Videos
  console.log('\n%c=== PHASE 2: VIDEOS ===', 'color:magenta;font-weight:bold');
  await runBatch(
    STORYBOARD.map((clip,i) => ({clip, img:imgs[i], vp:VIDEO_PROMPTS[i]})).filter(x=>x.img),
    ({clip,img,vp}) => genVideo(clip, img, vp),
    MAX_VID
  );

  console.log('%c\n🎉 ALLE 34 FERTIG! 🎉', 'color:gold;font-size:16px;font-weight:bold');
  console.log('Get results: copy(localStorage.getItem("stars_progress"))');
}

window._run = run;
run().catch(e => {
  console.error('%c❌', 'color:red', e.message);
  console.log('%cResume: window._run()', 'color:orange');
});
