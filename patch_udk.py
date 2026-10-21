#!/usr/bin/env python3
"""ใช้: python3 patch_udk.py index.html public/index.html
แก้ไฟล์ต้นฉบับ: realtime/login/ความปลอดภัย (ถ้าจุดไหนหาไม่เจอ จะหยุดและไม่เขียนไฟล์)"""
import re, sys
src = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
dst = sys.argv[2] if len(sys.argv) > 2 else 'index.fixed.html'
t = open(src, encoding='utf-8').read().replace('\r\n', '\n')
errs = []
def rep(old, new):
    global t
    pat = r'\s+'.join(re.escape(x) for x in old.split())
    n = len(re.findall(pat, t))
    if n != 1:
        errs.append((n, old[:70])); return
    t = re.sub(pat, lambda m: new, t, count=1)

# 1) ตัวจัดการ listener (ผูกหลัง login / ถอดตอน logout)
rep(r'''let fbDb = null, fbAuth = null;''', r'''let fbDb = null, fbAuth = null;
var UNSUB = [];
function listen(path, cb, err){ const r = fbDb.ref(path), h = r.on('value', cb, err); UNSUB.push(() => r.off('value', h)); }
function stopRealtime(){
  UNSUB.forEach(f => { try{ f(); }catch(e){} }); UNSUB = [];
  DBS.ready = false; DBS.last = {}; DBS.rs = undefined;
  ME.name = ''; ME.host = false; ME.role = 'viewer'; ME.routed = false; ME._pc = 0; ME._pk = ''; ME.uid = null; ME.email = '';
}''')

# 2) XSS ในแบนเนอร์คำเชิญ
rep(r'''if(ib) ib.innerHTML = `📩 <b>คุณได้รับคำเชิญให้เข้าสู่ตำแหน่ง: "${invitedRoleName}"</b><br>กรุณาเข้าสู่ระบบด้วยอีเมลของคุณเพื่อเริ่มทำงานทันที`;''',
    r'''if(ib) ib.textContent = '📩 คุณได้รับคำเชิญให้เข้าสู่ตำแหน่ง: "' + invitedRoleName + '" กรุณาเข้าสู่ระบบด้วยอีเมลของคุณเพื่อเริ่มทำงานทันที';''')

# 3) Gemini key + presence listeners -> เริ่มหลัง login เท่านั้น
rep(r'''if(fbDb){
  fbDb.ref('udk/config/geminiKey').on('value', s => {''', r'''function startGemini(){
  if(fbDb) listen('udk/config/geminiKey', s => {''')
rep(r'''if(fbDb){
  fbDb.ref('udk_presence').on('value', s => {''', r'''function startPresence(){
  if(fbDb) listen('udk_presence', s => {''')

# 4) Presence ทนเน็ตหลุด (.info/connected)
rep(r'''function updatePresence(){
  if(!fbDb || !ME.uid || !ME.email) return;
  const pRef = fbDb.ref('udk_presence/' + ME.uid);
  const info = { name: ME.name || ME.email, role: ME.role, email: ME.email, at: firebase.database.ServerValue.TIMESTAMP };
  pRef.set(info).catch(()=>{});
  pRef.onDisconnect().remove().catch(()=>{});
}''', r'''function updatePresence(){
  if(!fbDb || !ME.uid || !ME.email) return;
  const p = fbDb.ref('udk_presence/' + ME.uid), k = ME.name + '|' + ME.role;
  window._pi = { name: ME.name || ME.email, role: ME.role, email: ME.email, at: firebase.database.ServerValue.TIMESTAMP };
  if(!ME._pc){ ME._pc = 1; listen('.info/connected', s => { if(s.val() === true) p.onDisconnect().remove().then(() => p.set(window._pi)).catch(()=>{}); }); }
  if(ME._pk !== k){ ME._pk = k; p.set(window._pi).catch(()=>{}); }
}''')

# 5) listener หลักของข้อมูล
rep(r'''fbDb.ref('udk').on('value', s => {''', r'''listen('udk', s => {''')

# 6) auth handler: ไม่ตั้ง DBS.ready ก่อน snapshot แรก + บังคับยืนยันอีเมล
rep(r'''fbAuth.onAuthStateChanged(user => {
    if(user){''', r'''fbAuth.onAuthStateChanged(user => {
    stopRealtime();
    if(user && !user.emailVerified){
      user.sendEmailVerification().catch(()=>{});
      const em0 = user.email;
      fbAuth.signOut().then(() => { $('authErr').style.color = 'var(--cv)'; $('authErr').textContent = 'ส่งลิงก์ยืนยันอีเมลไปที่ ' + em0 + ' แล้ว กรุณากดยืนยันในอีเมล (ดูใน Junk ด้วย) แล้วเข้าสู่ระบบอีกครั้ง'; });
      return;
    }
    if(user){''')
rep(r'''DBS.ready = true;
      dbInit();
      meUpdate();
      refresh();''', r'''dbInit();
      startGemini(); startPresence();
      refresh();''')

# 7) เริ่มต้นไฟล์: ไม่เรียก dbInit ก่อน login + ดัก in-app browser + redirect result
rep(r'''persona();sim();dbInit();''', r'''persona();sim();
if(!fbDb) dbInit();
if(/Line\/|FBAN|FBAV|Instagram/i.test(navigator.userAgent)) $('authErr').textContent = 'เปิดลิงก์นี้ด้วย Chrome หรือ Safari แล้วค่อยเข้าสู่ระบบด้วย Google (LINE บล็อกการ Login ของ Google)';
if(fbAuth) fbAuth.getRedirectResult().catch(e => { $('authErr').textContent = 'เข้าสู่ระบบไม่สำเร็จ (' + (e.code || e.message) + ')'; });''')

# 8) Google login
rep(r'''$('authErr').textContent = 'กำลังเปิดหน้าต่าง Google...';''', r'''$('authErr').style.color = 'var(--bad)'; $('authErr').textContent = 'กำลังเปิดหน้าต่าง Google...';''')
rep(r'''if(e && (e.code === 'auth/popup-blocked' || e.code === 'auth/popup-closed-by-user' || e.code === 'auth/cancelled-popup-request')){''',
    r'''if(e && (e.code === 'auth/popup-blocked' || e.code === 'auth/cancelled-popup-request')){''')
rep(r'''$('authErr').textContent = 'เข้าด้วยป๊อปอัปไม่สำเร็จ กรุณาใช้อีเมลและรหัสผ่านด้านล่างแทน (' + (e.code || e.message) + ')';''',
    r'''const M = {'auth/unauthorized-domain':'โดเมนนี้ยังไม่ได้เพิ่มใน Firebase > Authentication > Settings > Authorized domains','auth/operation-not-allowed':'ยังไม่ได้เปิด Google ใน Sign-in method','auth/popup-closed-by-user':'ปิดหน้าต่าง Google ก่อนเข้าสู่ระบบเสร็จ','auth/operation-not-supported-in-this-environment':'เบราว์เซอร์/ที่เปิดไฟล์นี้ไม่รองรับ (ต้องเปิดผ่านลิงก์ https ใน Chrome/Safari)'};
    $('authErr').textContent = (M[e.code] || 'เข้าสู่ระบบด้วย Google ไม่สำเร็จ') + ' (' + (e.code || e.message) + ')';''')
rep(r'''$('authErr').textContent = 'กำลังเข้าสู่ระบบ...';''', r'''$('authErr').style.color = 'var(--bad)'; $('authErr').textContent = 'กำลังเข้าสู่ระบบ...';''')
rep(r'''$('authErr').textContent = 'กำลังตรวจสอบบัญชี...';''', r'''$('authErr').style.color = 'var(--bad)'; $('authErr').textContent = 'กำลังตรวจสอบบัญชี...';''')

# 9) สิทธิ์ checklist, เวลาจาก server, ซ่อน API key จาก URL
rep(r'''forEach(c=>c.onchange=()=>{c.checked?S.od.add(c.dataset.k):S.od.delete(c.dataset.k);sv();os()});''',
    r'''forEach(c=>c.onchange=()=>{if(!perm('edit')){deny();os();return}c.checked?S.od.add(c.dataset.k):S.od.delete(c.dataset.k);sv();os()});''')
rep(r'''set({j,by:actor,at:now})''', r'''set({j,by:actor,at:firebase.database.ServerValue.TIMESTAMP})''')
rep(r'''generateContent?key=${encodeURIComponent(GEMINI_KEY)}''', r'''generateContent''')

if errs:
    print('❌ หาจุดแก้ไม่เจอ/เจอซ้ำ (จำนวนที่พบ, ข้อความ):')
    for n, s in errs: print('  ', n, s)
    print('ไม่ได้เขียนไฟล์ ให้ตรวจว่าใช้ไฟล์ต้นฉบับที่ยังไม่ถูกแก้'); sys.exit(1)
import os
os.makedirs(os.path.dirname(os.path.abspath(dst)), exist_ok=True)
open(dst, 'w', encoding='utf-8').write(t)
print('✅ แพตช์ครบ 20 จุด ->', dst)
