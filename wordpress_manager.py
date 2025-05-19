import requests
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv
from pathlib import Path
import google.generativeai as genai

# Konfigurasi logging
logging.basicConfig(
    filename="logs/wordpress_manager.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class WordPressManager:
    """Kelas untuk mengelola website WordPress melalui REST API dengan integrasi Gemini AI."""

    def __init__(self):
        """Inisialisasi WordPressManager dengan kredensial dari file .env."""
        load_dotenv(dotenv_path=Path("config/.env"))
        self.site_url = os.getenv("WORDPRESS_URL").rstrip("/")
        self.api_url = f"{self.site_url}/wp-json/wp/v2"
        self.jwt_url = f"{self.site_url}/wp-json/jwt-auth/v1/token"
        self.username = os.getenv("WORDPRESS_USERNAME")
        self.password = os.getenv("WORDPRESS_PASSWORD")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.token = None
        self.headers = None
        self._validate_config()
        self.authenticate()
        self._configure_gemini()

    def _validate_config(self) -> None:
        """Validasi kredensial dan konfigurasi."""
        required = {
            "WORDPRESS_URL": self.site_url,
            "WORDPRESS_USERNAME": self.username,
            "WORDPRESS_PASSWORD": self.password,
            "GEMINI_API_KEY": self.gemini_api_key
        }
        for key, value in required.items():
            if not value:
                logger.error(f"Konfigurasi {key} tidak ditemukan di .env")
                raise ValueError(f"Konfigurasi {key} tidak ditemukan di .env")

    def _configure_gemini(self) -> None:
        """Konfigurasi Gemini API."""
        try:
            genai.configure(api_key=self.gemini_api_key)
            self.gemini_model = genai.GenerativeModel("gemini-1.5-flash")
            logger.info("Gemini API dikonfigurasi berhasil.")
        except Exception as e:
            logger.error(f"Gagal mengkonfigurasi Gemini API: {str(e)}")
            raise

    def authenticate(self) -> None:
        """Autentikasi ke WordPress menggunakan JWT."""
        try:
            payload = {"username": self.username, "password": self.password}
            response = requests.post(self.jwt_url, json=payload, timeout=10)
            response.raise_for_status()
            self.token = response.json().get("token")
            self.headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            logger.info("Autentikasi WordPress berhasil.")
        except requests.RequestException as e:
            logger.error(f"Autentikasi gagal: {str(e)}")
            raise Exception(f"Autentikasi gagal: {str(e)}")

    # --- Manajemen Tema ---
    def list_themes(self) -> List[Dict]:
        """Mendapatkan daftar tema yang terpasang."""
        try:
            url = f"{self.site_url}/wp-json/wp/v2/themes"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            logger.info("Berhasil mengambil daftar tema.")
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Gagal mengambil tema: {str(e)}")
            raise

    def activate_theme(self, theme_slug: str) -> Dict:
        """Mengaktifkan tema berdasarkan slug."""
        try:
            url = f"{self.site_url}/wp-json/wp/v2/settings"
            data = {"theme": theme_slug}
            response = requests.post(url, headers=self.headers, json=data, timeout=10)
            response.raise_for_status()
            logger.info(f"Tema {theme_slug} diaktifkan.")
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Gagal mengaktifkan tema {theme_slug}: {str(e)}")
            raise

    # --- Manajemen Menu ---
    def update_menu(self, menu_id: int, items: List[Dict]) -> Dict:
        """Memperbarui item menu."""
        try:
            url = f"{self.api_url}/menus/{menu_id}"
            response = requests.post(url, headers=self.headers, json={"items": items}, timeout=10)
            response.raise_for_status()
            logger.info(f"Menu ID {menu_id} diperbarui.")
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Gagal memperbarui menu ID {menu_id}: {str(e)}")
            raise

    # --- Manajemen Artikel dan Halaman ---
    def create_post(self, title: str, content: str, categories: List[int] = None,
                    featured_image_id: Optional[int] = None, status: str = "publish",
                    post_type: str = "post") -> Dict:
        """Membuat artikel atau halaman baru."""
        try:
            data = {
                "title": title,
                "content": content,
                "status": status,
                "type": post_type
            }
            if categories:
                data["categories"] = categories
            if featured_image_id:
                data["featured_media"] = featured_image_id

            url = f"{self.api_url}/{post_type}s"
            response = requests.post(url, headers=self.headers, json=data, timeout=10)
            response.raise_for_status()
            logger.info(f"{post_type.capitalize()} '{title}' dibuat.")
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Gagal membuat {post_type} '{title}': {str(e)}")
            raise

    def update_post(self, post_id: int, post_type: str = "post", title: Optional[str] = None,
                    content: Optional[str] = None, categories: List[int] = None,
                    featured_image_id: Optional[int] = None) -> Dict:
        """Memperbarui artikel atau halaman."""
        try:
            data = {}
            if title:
                data["title"] = title
            if content:
                data["content"] = content
            if categories:
                data["categories"] = categories
            if featured_image_id:
                data["featured_media"] = featured_image_id

            url = f"{self.api_url}/{post_type}s/{post_id}"
            response = requests.post(url, headers=self.headers, json=data, timeout=10)
            response.raise_for_status()
            logger.info(f"{post_type.capitalize()} ID {post_id} diperbarui.")
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Gagal memperbarui {post_type} ID {post_id}: {str(e)}")
            raise

    def delete_post(self, post_id: int, post_type: str = "post") -> Dict:
        """Menghapus artikel atau halaman."""
        try:
            url = f"{self.api_url}/{post_type}s/{post_id}"
            response = requests.delete(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            logger.info(f"{post_type.capitalize()} ID {post_id} dihapus.")
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Gagal menghapus {post_type} ID {post_id}: {str(e)}")
            raise

    # --- Manajemen Media ---
    def upload_media(self, file_path: str, alt_text: str = "", description: str = "") -> Dict:
        """Mengunggah media seperti gambar atau video."""
        try:
            url = f"{self.api_url}/media"
            headers = {"Authorization": self.headers["Authorization"]}
            with open(file_path, "rb") as file:
                files = {"file": (os.path.basename(file_path), file)}
                data = {"alt_text": alt_text, "description": description}
                response = requests.post(url, headers=headers, files=files, data=data, timeout=15)
            response.raise_for_status()
            logger.info(f"Media {file_path} diunggah.")
            return response.json()
        except (requests.RequestException, FileNotFoundError) as e:
            logger.error(f"Gagal mengunggah media {file_path}: {str(e)}")
            raise

    # --- Manajemen Pengguna ---
    def create_user(self, username: str, email: str, password: str, role: str) -> Dict:
        """Membuat pengguna baru."""
        try:
            data = {
                "username": username,
                "email": email,
                "password": password,
                "roles": [role]
            }
            url = f"{self.api_url}/users"
            response = requests.post(url, headers=self.headers, json=data, timeout=10)
            response.raise_for_status()
            logger.info(f"Pengguna {username} dibuat dengan peran {role}.")
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Gagal membuat pengguna {username}: {str(e)}")
            raise

    def update_user(self, user_id: int, email: Optional[str] = None, role: Optional[str] = None) -> Dict:
        """Memperbarui pengguna."""
        try:
            data = {}
            if email:
                data["email"] = email
            if role:
                data["roles"] = [role]
            url = f"{self.api_url}/users/{user_id}"
            response = requests.post(url, headers=self.headers, json=data, timeout=10)
            response.raise_for_status()
            logger.info(f"Pengguna ID {user_id} diperbarui.")
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Gagal memperbarui pengguna ID {user_id}: {str(e)}")
            raise

    def delete_user(self, user_id: int, reassign: Optional[int] = None) -> Dict:
        """Menghapus pengguna."""
        try:
            url = f"{self.api_url}/users/{user_id}"
            if reassign:
                url += f"?reassign={reassign}"
            response = requests.delete(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            logger.info(f"Pengguna ID {user_id} dihapus.")
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Gagal menghapus pengguna ID {user_id}: {str(e)}")
            raise

    # --- Backup dan Restore ---
    def backup_site(self, backup_path: str) -> str:
        """Membuat backup situs (simulasi, perlu plugin seperti UpdraftPlus untuk fungsi nyata)."""
        try:
            backup_dir = Path(backup_path)
            backup_dir.mkdir(parents=True, exist_ok=True)
            backup_file = backup_dir / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            with open(backup_file, "w") as f:
                f.write("Simulasi backup WordPress. Gunakan plugin seperti UpdraftPlus untuk backup nyata.")
            logger.info(f"Backup dibuat: {backup_file}")
            return str(backup_file)
        except Exception as e:
            logger.error(f"Gagal membuat backup: {str(e)}")
            raise

    # --- Integrasi Gemini AI untuk Pembuatan Artikel ---
    def generate_article_with_gemini(self, topic: str, length: str = "medium") -> Dict:
        """Menghasilkan artikel menggunakan Gemini AI."""
        try:
            length_map = {"short": 200, "medium": 500, "long": 1000}
            word_count = length_map.get(length, 500)
            prompt = (
                f"Buat artikel dalam bahasa Indonesia tentang '{topic}' dengan panjang sekitar {word_count} kata. "
                f"Gunakan gaya penulisan yang informatif dan menarik, cocok untuk blog WordPress. "
                f"Sertakan judul yang relevan dan konten yang terstruktur dengan paragraf yang jelas."
            )
            response = self.gemini_model.generate_content(prompt)
            content = response.text
            # Asumsi konten dimulai dengan judul (misalnya, dalam format markdown atau teks)
            lines = content.split("\n")
            title = lines[0].strip("# ").strip() if lines[0].startswith("#") else topic.title()
            article_content = "\n".join(lines[1:]).strip() if lines[0].startswith("#") else content
            logger.info(f"Artikel tentang '{topic}' dihasilkan oleh Gemini AI.")
            return {"title": title, "content": article_content}
        except Exception as e:
            logger.error(f"Gagal menghasilkan artikel dengan Gemini AI: {str(e)}")
            raise
