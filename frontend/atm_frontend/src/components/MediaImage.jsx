/**
 * MediaImage Component
 * 
 * Displays images from the Render backend with proper error handling
 * and fallback support for cross-domain media serving.
 */
import React, { useState, useEffect } from 'react';
import { ensureAbsoluteUrl } from '../utils/mediaUrlHelper';

const MediaImage = ({
  src,
  alt = 'Image',
  className = '',
  imgClassName = 'w-full h-full object-cover',
  style = {},
  fallbackSrc = null,
  onLoad = null,
  onError = null,
  loading = 'lazy',
  ...props
}) => {
  const [imageSrc, setImageSrc] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);

  useEffect(() => {
    if (src) {
      // Ensure the URL is absolute
      const absoluteUrl = ensureAbsoluteUrl(src);
      setImageSrc(absoluteUrl);
      setHasError(false);
      setIsLoading(true);
    }
  }, [src]);

  const handleLoad = (e) => {
    setIsLoading(false);
    if (onLoad) {
      onLoad(e);
    }
  };

  const handleError = (e) => {
    console.warn(`Failed to load image from: ${imageSrc}`);
    setIsLoading(false);
    setHasError(true);

    if (fallbackSrc) {
      const absoluteFallback = ensureAbsoluteUrl(fallbackSrc);
      setImageSrc(absoluteFallback);
      setHasError(false);
    }

    if (onError) {
      onError(e);
    }
  };

  if (!imageSrc) {
    return (
      <div
        className={`bg-gray-200 flex items-center justify-center ${className}`}
        style={style}
      >
        <span className="text-gray-500 text-sm">No image</span>
      </div>
    );
  }

  return (
    <div className={`relative ${className}`} style={style}>
      {isLoading && (
        <div className="absolute inset-0 bg-gray-200 animate-pulse rounded" />
      )}
      <img
        src={imageSrc}
        alt={alt}
        onLoad={handleLoad}
        onError={handleError}
        loading={loading}
        className={`${imgClassName} ${hasError ? 'hidden' : ''}`}
        {...props}
      />
      {hasError && (
        <div className="absolute inset-0 bg-gray-200 flex items-center justify-center rounded">
          <span className="text-gray-500 text-sm">Failed to load image</span>
        </div>
      )}
    </div>
  );
};

export default MediaImage;
