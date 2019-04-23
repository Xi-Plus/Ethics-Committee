import os

from Kamisu66 import EthicsCommitteeExtension


class DownloadProfilePhoto(EthicsCommitteeExtension):
    def __init__(self, savepath):
        self.savepath = savepath

    def main(self, EC):
        if not EC.update.message:
            return

        if EC.update.message.new_chat_members:
            photos = EC.bot.get_user_profile_photos(
                EC.update.message.new_chat_members[0].id, limit=1)

            if photos.total_count == 0:
                # no photo
                return

            filepath = os.path.join(self.savepath, '{}.jpg'.format(
                EC.update.effective_user.id))
            photos.photos[0][0].get_file().download(filepath)


def __mainclass__():
    return DownloadProfilePhoto
