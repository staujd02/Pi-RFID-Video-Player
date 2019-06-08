from dataLinker import DataLinker


class CardToVideoLinker(DataLinker):

    def pair(self, cardID, videoName):
        try:
            super(CardToVideoLinker, self).pair(
                cardID, videoName, self.__checkVideoIsActive)
        except super(CardToVideoLinker, self).PairPreCheckFailed:
            raise self.CannotPairToInactiveVideo(videoName, cardID)

    def __checkVideoIsActive(self, video):
        return video[2] == 'True'

    class CannotPairToInactiveVideo(Exception):

        def __init__(self, video, card):
            self.video = video
            self.card = card
