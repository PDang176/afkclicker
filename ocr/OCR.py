from abc import ABC, abstractmethod

class OCR(ABC):
  @abstractmethod
  def preprocess_image(self, image):
    pass

  @abstractmethod
  def extract_text(self, image):
    pass