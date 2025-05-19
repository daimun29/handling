from wordpress_manager import WordPressManager
import logging

def main():
    # Inisialisasi logging untuk main
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    try:
        # Inisialisasi WordPressManager
        wp = WordPressManager()

        # Contoh penggunaan: Manajemen tema
        themes = wp.list_themes()
        logger.info(f"Tema yang tersedia: {[theme['slug'] for theme in themes]}")
        # wp.activate_theme("twentytwentyfive")

        # Contoh penggunaan: Manajemen menu
        menu_items = [
            {"title": "Beranda", "url": "/"},
            {"title": "Tentang", "url": "/tentang"}
        ]
        # wp.update_menu(menu_id=1, items=menu_items)

        # Contoh penggunaan: Membuat artikel dengan Gemini AI
        article = wp.generate_article_with_gemini(topic="Manfaat Teknologi AI", length="medium")
        post = wp.create_post(
            title=article["title"],
            content=article["content"],
            categories=[1],  # Ganti dengan ID kategori yang valid
            status="draft"
        )
        logger.info(f"Artikel dibuat dengan ID: {post['id']}")

        # Contoh penggunaan: Mengunggah media
        media = wp.upload_media(
            file_path="path/to/image.jpg",  # Ganti dengan path file yang valid
            alt_text="Gambar contoh",
            description="Deskripsi gambar"
        )
        logger.info(f"Media diunggah dengan ID: {media['id']}")

        # Contoh penggunaan: Memperbarui artikel dengan gambar unggulan
        wp.update_post(
            post_id=post["id"],
            featured_image_id=media["id"],
            status="publish"
        )
        logger.info(f"Artikel ID {post['id']} diperbarui dan diterbitkan.")

        # Contoh penggunaan: Manajemen pengguna
        user = wp.create_user(
            username="pengguna_baru",
            email="baru@example.com",
            password="securepassword123",
            role="editor"
        )
        logger.info(f"Pengguna dibuat dengan ID: {user['id']}")

        # Contoh penggunaan: Backup
        backup_file = wp.backup_site(backup_path="backups")
        logger.info(f"Backup disimpan di: {backup_file}")

        # Contoh penggunaan: Menghapus artikel
        wp.delete_post(post_id=post["id"])
        logger.info(f"Artikel ID {post['id']} dihapus.")

        # Contoh penggunaan: Menghapus pengguna
        wp.delete_user(user_id=user["id"], reassign=1)
        logger.info(f"Pengguna ID {user['id']} dihapus.")

    except Exception as e:
        logger.error(f"Terjadi kesalahan: {str(e)}")

if __name__ == "__main__":
    main()
