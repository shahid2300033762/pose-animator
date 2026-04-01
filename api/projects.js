export default function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();

  const projects = [
    {
      id: 1,
      title: "Neo-Modern Flow",
      image: "https://lh3.googleusercontent.com/aida-public/AB6AXuDSmbfqMADZArvfVOk09ObQKpn-Lmotv_4gZ1qWILGSq7zXUVqCs0p_d9RTj8avPMCFInY9-S0E9e0CrOTkk8u6aICgQ4kWbPnke5Jfhd9xbdK4ZBJMpR0-1WtrwPoUDKDckHb1dRMKWCsVA8w5w9hmBLVIP1jKRreSL2YEwVpmaKqg30MGUyTbe5DTmlRUxkOQ23LSRe8w86oTBD_x-vJrOMbr3ulBF3NRRYmNBst3YOnisSnq-PxSpWwua4H8jZxbPW4tjrovz18",
      youtubeLink: "https://youtu.be/lKScqfdcN_s?si=DdbhfybisGLEkcIy",
      tags: ["4K RAW", "60 FPS"]
    },
    {
      id: 2,
      title: "Kinetic Study 09",
      image: "https://lh3.googleusercontent.com/aida-public/AB6AXuDNzJR4yj7Hb1jgCGEXH90EO5a0cHiiVHyJ5loxU_NiSRwAfzDUyu3VYMDZhXLW4SsmUX-kIgEjA_2VuqV96csEy28qC7hlFCxXUmLrPfw1nwyf9luOhYk84i0MOByqNauwevrogKkcfUo2uX2StkVInmcATrKgISxlc_njFPT84acWVSi14KjeGoK1yJ_NaIZs-NOqGAp8admeHiEEjnxXhI-ldGoDM4HuZ8Br4uyFNg42z9vW1M8wH4xL5Zi_mwiWrMk-aSLTKtE",
      youtubeLink: "https://youtube.com/shorts/_XFwdaIxIdE?si=635vXq4f80uTXYy-",
      tags: ["Skeletal", "Experimental"]
    }
  ];
  res.status(200).json(projects);
}
