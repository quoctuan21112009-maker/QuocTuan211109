# backend.py
# Flask API to run scripts referenced by id (based on mm.py mapping)
# WARNING: Running arbitrary remote code is dangerous. Use only on trusted code.
from flask import Flask, request, jsonify
import requests, subprocess, tempfile, os, shlex, sys, uuid, time

app = Flask(__name__)

# Mapping: id (string) -> raw github url (taken from mm.py)
SCRIPT_MAP = {
    "00": "https://raw.githubusercontent.com/Khanh23047/thoattool/main/.github/workflows/main.yml",
    "1":  "https://raw.githubusercontent.com/Khanh23047/TDS-TIKTOK-V1/main/tool.py",
    "2":  "https://raw.githubusercontent.com/Khanh23047/Tdstikv2/main/00.py",
    "3":  "https://raw.githubusercontent.com/Khanh23047/Tik-tiknow/main/1.py",
    "4":  "https://raw.githubusercontent.com/Khanh23047/Tds3.12/main/12.py",
    "5":  "https://raw.githubusercontent.com/Khanh23047/TDS-IG/main/3.py",
    "6":  "https://raw.githubusercontent.com/Khanh23047/Mktds/main/4.py",
    "7":  "https://raw.githubusercontent.com/Khanh23047/thoattool/main/.github/workflows/main.yml",
    "8":  "https://raw.githubusercontent.com/Khanh23047/Ttcfb312/main/ttcfb312.py",
    "9":  "https://raw.githubusercontent.com/Khanh23047/TTCPR5/main/5.py",
    "10": "https://raw.githubusercontent.com/Khanh23047/TTC-IG/main/6.py",
    "11": "https://raw.githubusercontent.com/Khanh23047/Spamsmsv1/main/sms.py",
    "12": "https://raw.githubusercontent.com/Khanh23047/Spamsmsv2/main/smsv2.py",
    "13": "https://raw.githubusercontent.com/Khanh23047/Daomail/main/8.py",
    "14": "https://raw.githubusercontent.com/Khanh23047/Full-mail/main/vietcode_toolmeow.py",
    "15": "https://raw.githubusercontent.com/Khanh23047/Checklivedie/main/p.py",
    "16": "https://raw.githubusercontent.com/Khanh23047/checkvali/main/10.py",
    "17": "https://raw.githubusercontent.com/Khanh23047/Reggrn/main/Reggrn",
    "18": "https://raw.githubusercontent.com/Khanh23047/LIKE-FACEBOOK-/main/p.py",
    "19": "https://raw.githubusercontent.com/Khanh23047/Ketbangoiy/main/p.py",
    "20": "https://raw.githubusercontent.com/Khanh23047/Shareaocookie/main/share.py",
    "21": "https://raw.githubusercontent.com/Khanh23047/Shareaotoken/main/shareao.py",
    "22": "https://raw.githubusercontent.com/Khanh23047/Viewpr5/main/p.py",
    "23": "https://raw.githubusercontent.com/Khanh23047/Nuoi-fb/main/10.py",
    "24": "https://raw.githubusercontent.com/Khanh23047/Checklivedieproxy/main/p.py",
    "25": "https://raw.githubusercontent.com/Khanh23047/Checklivediev2/main/p.py",
    "26": "https://raw.githubusercontent.com/Khanh23047/Daoprxv2/main/p.py",
    "27": "https://raw.githubusercontent.com/Khanh23047/Daoproxyv3/main/p.py",
    "28": "https://raw.githubusercontent.com/Khanh23047/Daoproxyv4/main/p.py",
    "29": "https://raw.githubusercontent.com/Khanh23047/Daoproxyv4vip/main/p.py",
    "30": "https://raw.githubusercontent.com/Khanh23047/Nh-y-c-d-u/main/p.py",
    "31": "https://raw.githubusercontent.com/Khanh23047/Nhaykodau/main/p.py",
    "32": "https://raw.githubusercontent.com/Khanh23047/Reotentrongbox/main/p.py",
    "33": "https://raw.githubusercontent.com/Khanh23047/Nhaycodelag/main/p.py",
    "34": "https://raw.githubusercontent.com/Khanh23047/Treoso/main/p.py",
    "35": "https://raw.githubusercontent.com/Khanh23047/Nhaydis/main/p.py",
    "36": "https://raw.githubusercontent.com/KhanhNguyen9872/hyperion_deobfuscate/main/hyperion_deobf.py",
    "37": "https://raw.githubusercontent.com/KhanhNguyen9872/kramer-specter_deobf/main/kramer-specter-deobf.py",
    "38": "https://raw.githubusercontent.com/KhanhNguyen9872/dump_marshal_py/main/dump_marshal.py",
    "39": "https://raw.githubusercontent.com/KhanhNguyen9872/Convert_Marshal-PYC/main/cv_marshal_pyc.py",
    "40": "https://raw.githubusercontent.com/Khanh23047/Encode-MZB/main/en.py",
    "41": "https://raw.githubusercontent.com/Khanh23047/Encode-Emoji-/main/p.py",
    "42": "https://raw.githubusercontent.com/Khanh23047/Encode-ejuly-DUYKHANH/main/encode.py",
    "43": "https://raw.githubusercontent.com/Khanh23047/Encode-MEO/refs/heads/main/meo.py",
    "44": "https://raw.githubusercontent.com/Khanh23047/Golike/main/golike.py",
    "45": "https://raw.githubusercontent.com/Khanh23047/thoattool/main/.github/workflows/main.yml",
    "46": "https://raw.githubusercontent.com/Khanh23047/thoattool/main/.github/workflows/main.yml",
    "47": "https://raw.githubusercontent.com/Khanh23047/Golike-ig/main/p.py",
    "48": "https://raw.githubusercontent.com/Khanh23047/Golike-Twitter-/main/p.py",
    "49": "https://raw.githubusercontent.com/Khanh23047/thoattool/main/.github/workflows/main.yml",
    "50": "https://raw.githubusercontent.com/Khanh23047/thoattool/main/.github/workflows/main.yml",
    "51": "https://raw.githubusercontent.com/Khanh23047/thoattool/main/.github/workflows/main.yml",
    "52": "https://raw.githubusercontent.com/Khanh23047/thoattool/main/.github/workflows/main.yml",
    "53": "https://raw.githubusercontent.com/Khanh23047/Tool-vlong/main/p.py",
    "54": "https://raw.githubusercontent.com/Khanh23047/Tool-trinh-huong/main/huong.py",
    "55": "https://raw.githubusercontent.com/Khanh23047/Full-mail/main/vietcode_toolmeow.py",
    "56": "https://raw.githubusercontent.com/Khanh23047/Tool-hdt/main/p.py",
    "57": "https://raw.githubusercontent.com/Khanh23047/Tool-lkz/main/p.py",
    "58": "https://raw.githubusercontent.com/Khanh23047/Tool-jray/main/haha.py",
    "59": "https://raw.githubusercontent.com/Khanh23047/Buff-mem-FB/main/10.py",
    "60": "https://raw.githubusercontent.com/Khanh23047/Getcookie-pro5/main/10.py",
    "61": "https://raw.githubusercontent.com/Khanh23047/Buff-member-fb/main/10.py",
    "62": "https://raw.githubusercontent.com/Khanh23047/Buff-member-fb/main/10.py",
    "63": "https://raw.githubusercontent.com/Khanh23047/Reg-pro5-vip/main/reg.py",
    "64": "https://raw.githubusercontent.com/Khanh23047/Rutgonlink/main/10.py",
    "65": "https://raw.githubusercontent.com/Khanh23047/Phanhoilink/main/10.py",
    "66": "https://raw.githubusercontent.com/Khanh23047/L-c-Link-T-File/main/10.py",
    "67": "https://raw.githubusercontent.com/Khanh23047/Reg-fb/main/10.py",
    "68": "https://raw.githubusercontent.com/Khanh23047/Chuyenquyen-chapnhan/main/10.py",
    "69": "https://raw.githubusercontent.com/Khanh23047/Kichhoatpage/main/10.py",
    "70": "https://raw.githubusercontent.com/Khanh23047/Get-token/main/10.py",
    "71": "https://raw.githubusercontent.com/Khanh23047/DOSS-WEB/main/dos.py",
}

@app.route("/")
def home():
    return jsonify({"ok": True, "info": "QuocTuan Tool Backend. POST /run with json {id: '1'}"})

@app.route("/list")
def get_list():
    # return mapping keys and friendly names (small preview)
    names = {
      "1":"TDS TikTok V1","2":"TDS TikTok V2","3":"TDS TikTok & Now",
      # ... (you can expand names if desired)
    }
    return jsonify({"available_ids": list(SCRIPT_MAP.keys()), "names_sample": names})

@app.route("/run", methods=["POST"])
def run_script():
    data = request.get_json() or {}
    id_ = str(data.get("id","")).strip()
    if not id_ or id_ not in SCRIPT_MAP:
        return jsonify({"ok": False, "error": "Missing or invalid id"}), 400

    url = SCRIPT_MAP[id_]
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return jsonify({"ok": False, "error": f"Failed to fetch script from {url} (status {r.status_code})"}), 502
        script_text = r.text

        # Save to a temp file
        tmpdir = tempfile.gettempdir()
        fname = os.path.join(tmpdir, f"script_{id_}_{uuid.uuid4().hex}.py")
        with open(fname, "w", encoding="utf-8") as f:
            f.write(script_text)

        # Run in subprocess with timeout and capture output
        # WARNING: this executes remote code — dangerous. We set timeout (e.g., 20s).
        timeout_seconds = 20
        try:
            # Use sys.executable to ensure same Python interpreter
            proc = subprocess.run([sys.executable, fname],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  text=True,
                                  timeout=timeout_seconds)
            out = proc.stdout
            err = proc.stderr
            result = {"ok": True, "id": id_, "url": url, "stdout": out, "stderr": err, "returncode": proc.returncode}
        except subprocess.TimeoutExpired as e:
            result = {"ok": False, "error": "Execution timed out", "timeout_seconds": timeout_seconds}
        except Exception as e:
            result = {"ok": False, "error": f"Execution failed: {e}"}
        finally:
            # Clean up file
            try:
                os.remove(fname)
            except:
                pass

        return jsonify(result)

    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

if __name__ == "__main__":
    # For local testing
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))