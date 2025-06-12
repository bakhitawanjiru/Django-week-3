from django.core.management.base import BaseCommand
from PIL import Image
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Creates a default profile picture'

    def handle(self, *args, **kwargs):
        # Ensure the directory exists
        avatar_dir = os.path.join(settings.MEDIA_ROOT, 'profile_pics')
        os.makedirs(avatar_dir, exist_ok=True)
        
        avatar_path = os.path.join(avatar_dir, 'default.jpg')
        
        # Create a simple blue square as default avatar
        img = Image.new('RGB', (200, 200), color='#4A90E2')
        img.save(avatar_path, 'JPEG')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created default avatar at {avatar_path}')
        )