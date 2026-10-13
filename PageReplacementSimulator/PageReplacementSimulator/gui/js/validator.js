/**
 * validator.js
 * -------------
 * Input validation for the GUI, mirroring core/validator.py exactly so the
 * GUI rejects/accepts the same inputs as the CLI and shows the same style
 * of message.
 */

class ValidationError extends Error {}

function parseReferenceString(rawText) {
  if (rawText === null || rawText === undefined || rawText.trim() === "") {
    throw new ValidationError(
      "Reference string cannot be empty. Enter page numbers separated by commas or spaces, e.g. 7, 0, 1, 2, 0, 3, 0, 4"
    );
  }

  const tokens = rawText.replace(/,/g, " ").split(/\s+/).filter((t) => t !== "");
  if (tokens.length === 0) {
    throw new ValidationError("Reference string cannot be empty.");
  }

  const pages = [];
  for (const tok of tokens) {
    if (!/^-?\d+$/.test(tok)) {
      throw new ValidationError(
        `Invalid page number '${tok}'. Only non-negative integers are allowed in the reference string.`
      );
    }
    const value = parseInt(tok, 10);
    if (value < 0) {
      throw new ValidationError(`Invalid page number '${tok}'. Page numbers cannot be negative.`);
    }
    pages.push(value);
  }
  return pages;
}

function parseFrameCount(rawValue) {
  const text = String(rawValue).trim();
  if (!/^\d+$/.test(text)) {
    throw new ValidationError(`Number of frames must be a whole number, got '${rawValue}'.`);
  }
  const frames = parseInt(text, 10);
  if (frames < 1) {
    throw new ValidationError("Number of frames must be at least 1.");
  }
  if (frames > 50) {
    throw new ValidationError("Number of frames is unreasonably large (max supported is 50).");
  }
  return frames;
}

function validateInputs(rawReferenceString, rawFrameCount) {
  const referenceString = parseReferenceString(rawReferenceString);
  const frameCount = parseFrameCount(rawFrameCount);
  return { referenceString, frameCount };
}
