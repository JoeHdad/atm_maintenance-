/**
 * Media URL Helper Utility
 * 
 * Handles media file URLs from the Render backend.
 * Ensures images and PDFs from the backend API are displayed correctly
 * even when the frontend is hosted on a different domain (Hostinger).
 */

/**
 * Check if a URL is already absolute
 * @param {string} url - URL to check
 * @returns {boolean} True if URL is absolute
 */
export const isAbsoluteUrl = (url) => {
  if (!url) return false;
  return url.startsWith('http://') || url.startsWith('https://');
};

/**
 * Get the media base URL from environment or API response
 * @returns {string} Base URL for media files
 */
export const getMediaBaseUrl = () => {
  // Use the API base URL as the media base URL
  // The backend sends absolute URLs, so we don't need to construct them
  return process.env.REACT_APP_API_URL || window.location.origin;
};

/**
 * Ensure a media URL is absolute
 * If the URL is already absolute, return it as-is
 * If it's relative, prepend the media base URL
 * 
 * @param {string} url - Media URL (absolute or relative)
 * @returns {string} Absolute URL
 */
export const ensureAbsoluteUrl = (url) => {
  if (!url) return null;
  
  // If already absolute, return as-is
  if (isAbsoluteUrl(url)) {
    return url;
  }
  
  // If relative, prepend the media base URL
  const baseUrl = getMediaBaseUrl();
  const normalizedUrl = url.startsWith('/') ? url : `/${url}`;
  
  return `${baseUrl}${normalizedUrl}`;
};

/**
 * Get a safe image URL with fallback
 * @param {string} url - Image URL
 * @param {string} fallbackUrl - Fallback URL if primary fails
 * @returns {string} Safe image URL
 */
export const getSafeImageUrl = (url, fallbackUrl = null) => {
  if (!url) return fallbackUrl;
  return ensureAbsoluteUrl(url);
};

/**
 * Get a safe PDF URL with fallback
 * @param {string} url - PDF URL
 * @param {string} fallbackUrl - Fallback URL if primary fails
 * @returns {string} Safe PDF URL
 */
export const getSafePdfUrl = (url, fallbackUrl = null) => {
  if (!url) return fallbackUrl;
  return ensureAbsoluteUrl(url);
};

/**
 * Handle image load error with fallback
 * @param {Event} event - Image load error event
 * @param {string} fallbackUrl - Fallback image URL
 */
export const handleImageError = (event, fallbackUrl = null) => {
  if (fallbackUrl) {
    event.target.src = fallbackUrl;
  } else {
    // Hide image if no fallback
    event.target.style.display = 'none';
  }
  console.warn('Image failed to load:', event.target.src);
};

/**
 * Validate media URL accessibility
 * @param {string} url - URL to validate
 * @returns {Promise<boolean>} True if URL is accessible
 */
export const validateMediaUrl = async (url) => {
  if (!url) return false;
  
  try {
    const response = await fetch(url, {
      method: 'HEAD',
      mode: 'no-cors', // Allow cross-origin
    });
    return response.ok || response.status === 0; // 0 for no-cors
  } catch (error) {
    console.error('Media URL validation failed:', error);
    return false;
  }
};

/**
 * Get image dimensions from URL
 * @param {string} url - Image URL
 * @returns {Promise<{width: number, height: number}>} Image dimensions
 */
export const getImageDimensions = (url) => {
  return new Promise((resolve, reject) => {
    const img = new Image();
    
    img.onload = () => {
      resolve({
        width: img.width,
        height: img.height,
      });
    };
    
    img.onerror = () => {
      reject(new Error(`Failed to load image: ${url}`));
    };
    
    img.src = url;
  });
};

const mediaUrlHelper = {
  isAbsoluteUrl,
  getMediaBaseUrl,
  ensureAbsoluteUrl,
  getSafeImageUrl,
  getSafePdfUrl,
  handleImageError,
  validateMediaUrl,
  getImageDimensions,
};

export default mediaUrlHelper;
