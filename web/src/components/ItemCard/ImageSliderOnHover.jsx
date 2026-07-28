import React, { useState } from 'react';
import './ImageSliderOnHover.css';

const ImageSliderOnHover = ({ images, alt = "photo img" }) => {
  const [activeIndex, setActiveIndex] = useState(0);

  if (!images || images.length === 0) return null;

  return (
    <div className="hover-slider">
      <img 
        src={images[activeIndex]} 
        alt={`${alt} ${activeIndex + 1}`} 
        className="hover-slider__image" 
      />

      <div className="hover-slider__hover-zones">
        {images.map((_, index) => (
          <div
            key={index}
            className="hover-slider__zone"
            onMouseEnter={() => setActiveIndex(index)}
          />
        ))}
      </div>

      {images.length > 1 && (
        <div className="hover-slider__indicators">
          {images.map((_, index) => (
            <span
              key={index}
              className={`hover-slider__indicator ${
                index === activeIndex ? 'is-active' : ''
              }`}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default ImageSliderOnHover;