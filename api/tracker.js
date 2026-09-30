export default async function handler(req, res) {
  // ตั้งค่า CORS Header ให้เรียกใช้งานได้ปลอดภัย
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,PATCH,DELETE,POST,PUT');
  res.setHeader(
    'Access-Control-Allow-Headers',
    'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version'
  );

  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  // URL ของ Google Apps Script Web App
  const GAS_URL = "https://script.google.com/macros/s/AKfycbwP_tk7U46Q3MdTMvVMR3MnS8oZYhbVR5cmEqTkufWl9FGwBX-I0LHiY0Vhajfl6ZB3NA/exec";

  try {
    const action = req.query.action || (req.body && req.body.action);
    const payload = req.query.payload || (req.body && req.body.payload ? JSON.stringify(req.body.payload) : "{}");

    // ยิงคำขอต่อไปยัง Google Apps Script โดยอนุญาตให้ Follow Redirect อัตโนมัติ
    const targetUrl = `${GAS_URL}?action=${encodeURIComponent(action)}&payload=${encodeURIComponent(payload)}`;
    
    const response = await fetch(targetUrl, {
      method: 'GET',
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json'
      },
      redirect: 'follow'
    });

    const textData = await response.text();

    // ตรวจสอบว่า Google ส่งกลับมาเป็น JSON หรือไม่
    try {
      const jsonData = JSON.parse(textData);
      return res.status(200).json(jsonData);
    } catch (parseErr) {
      console.error("Non-JSON response from Google:", textData);
      return res.status(502).json({
        status: "ERROR",
        message: "Google Apps Script ส่งข้อมูลกลับมาไม่ถูกต้อง (อาจติด Rate Limit หรือ 404)",
        raw: textData.substring(0, 300)
      });
    }
  } catch (error) {
    console.error("Proxy Error:", error);
    return res.status(500).json({ status: "ERROR", message: error.message });
  }
}
