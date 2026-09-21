import {
  joiningPositions,
  type CharacterName,
  type JoiningPosition,
} from "./misc.ts";
import type { WrittenUnitID } from "./writtenUnits";
import { isVariantRef, type FVS, type VariantData } from "./variants.ts";

/**
 * A letter that lies outside every writing system: no character of the data is written
 * with its written units, so the character table is told what it draws.
 */
export type OutsideLetterData = {
  /** The written units the joining position is written with, or the position it borrows its form from. */
  written: VariantData["written"];
  /** Required for fonts, but not recommended for newly generated texts. See also: https://unicode.org/Public/16.0.0/ucd/DoNotEmit.txt */
  unrecommended?: true;
};

/** The letters that lie outside every writing system, by character name, joining position, and FVS. */
export type OutsideLetters = Record<
  CharacterName,
  Record<JoiningPosition, Partial<Record<FVS, OutsideLetterData>>>
>;

/**
 * The letters that lie outside every writing system, keyed by character name and by joining
 * position the way the variants of a character are, which the character table lists by code
 * point along with the characters of the writing systems.
 */
export const outsideLetters: OutsideLetters = {
  "MONGOLIAN LETTER CHA WITH TWO DOTS": {
    isol: { "0": { written: ["init", 0] } },
    init: { "0": { written: ["Cx"] } },
    medi: { "0": { written: ["Cx"] } },
    fina: { "0": { written: ["Cx"] } },
  },
  "MONGOLIAN LETTER TODO ALI GALI TA": {
    isol: { "0": { written: ["init", 0] } },
    init: { "0": { written: ["Dz"], unrecommended: true } },
    medi: { "0": { written: ["Dz"], unrecommended: true } },
    fina: { "0": { written: ["medi", 0] } },
  },
};

/** The written units those letters are drawn with, which no character of the data writes. */
export const outsideUnits: WrittenUnitID[] = [
  ...new Set(
    Object.values(outsideLetters).flatMap((positionToFVSToData) =>
      joiningPositions.flatMap((position) =>
        Object.values(positionToFVSToData[position]).flatMap(
          (data: OutsideLetterData) =>
            isVariantRef(data.written) ? [] : data.written,
        ),
      ),
    ),
  ),
];
