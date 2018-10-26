package edu.gatech.seclass;

import java.util.HashMap;
import java.util.Map;

/**
 * This is an implementation class for MyCustomStringInterface interface
 *
 * @author Rufus
 */
public class MyCustomString implements MyCustomStringInterface {
    private String currentStr; // Private String variable to hold current string content
    private static Map<Character, String> englishNameDigitMap; // Static englishNameDigitMap variable to hold 0-9 digit character and its English name

    public MyCustomString() {
        englishNameDigitMap = new HashMap<>();
        englishNameDigitMap.put('0', "zero");
        englishNameDigitMap.put('1', "one");
        englishNameDigitMap.put('2', "two");
        englishNameDigitMap.put('3', "three");
        englishNameDigitMap.put('4', "four");
        englishNameDigitMap.put('5', "five");
        englishNameDigitMap.put('6', "six");
        englishNameDigitMap.put('7', "seven");
        englishNameDigitMap.put('8', "eight");
        englishNameDigitMap.put('9', "nine");
    }

    // Get current string content
    @Override
    public String getString() {
        return currentStr;
    }

    // Set current string content with parameter string
    @Override
    public void setString(String string) {
        this.currentStr = string;
    }

    /**
     * Returns the number of numbers in the current string, where a number is defined as a
     * contiguous sequence of digits.
     *
     * If the current string is null, empty, or unset, the method should return 0.
     *
     * Examples:
     * - countDuplicates would return 2 for string "My numbers are 11 and 96".
     *
     * @return Number of numbers in the current string
     */
    @Override
    public int countDuplicates() {
        int total = 0; // total number of numbers, initial set with 0
        boolean prevDigitIsContiguous = false; // check previous digit is true or false, initial set with false

        // If the current string is null, empty, return total=0 directly
        if (currentStr == null || currentStr.length() ==0) return total;

        // Scan through each character in currentStr
        for (Character currentCharacter :  currentStr.toCharArray()) {
            // Check current digit is true or false using Character.isDigit
            boolean booleanCurrentDigit = Character.isDigit(currentCharacter);

            if (booleanCurrentDigit == true) {
                // Check previous digit is contiguous digit or not, increment total if current digit is true and previous digit is false
                if (prevDigitIsContiguous == false) {
                    total++;
                    prevDigitIsContiguous = true; // Set contiguous flag with true
                }
            } else {
                // Set contiguous flag with false
                prevDigitIsContiguous = false;
            }
        }

        return total; // return total number of numbers
    }

    
    @Override
    public String addDigits(int n, boolean positive) {
        // Throw NullPointerException, if the current string is null
        if (currentStr == null) throw new NullPointerException("The current string is null");

        // Throw MyIndexOutOfBoundsException, if n is greater than the string length, and the current string is not null
        if (n > currentStr.length()) throw new MyIndexOutOfBoundsException("Parameter n is greater than length of current string");

        // Throw IllegalArgumentException, if "n" less than or equal to zero, and the current string is not null
        if (n <= 0) throw new IllegalArgumentException("Parameter n is less than or equal to zero");

        String result = "";
        int stepper = n; // Save stepper first
        if (positive) {
            // Return the string with the positions
            while (true && n <= currentStr.length()) {
                result += this.currentStr.charAt(n - 1); // Parameter n is based on 1, so need to minus 1 to align up with 0-based index for accessing a character in a string
                n += stepper;
            }
        } else {
            // Return the string except the positions
            for (int i = 0; i < currentStr.length(); i++) {
                if (i + 1 == n) {
                    n += stepper; // Only do this when i + 1 == n
                } else {
                    result += this.currentStr.charAt(i); // Append current character when current position is not equal to the parameter n
                }
            }
        }

        return result;
    }

    /**
     * Replace the individual digits in the current string, between startPosition and endPosition
     * (included), with the corresponding English names of those digits, with no letters
     * capitalized. The first character in the string is considered to be in Position 1.
     * Contiguous digits will be surrounded by asterisks and each digit will be converted individually.
     *
     * Examples:
     * - String 460 would be converted to *foursixzero*
     * - String 416 would be converted to *fouronesix*
     *
     * @param startPosition Position of the first character to consider
     * @param endPosition   Position of the last character to consider

     * @throws IllegalArgumentException    If "startPosition" < 1 or "startPosition" > "endPosition"
     * @throws MyIndexOutOfBoundsException If "endPosition" is out of bounds (greater than the length of the string)
     * and 1 <= "startPosition" < "endPosition"
     */
    @Override
    public void FlipLetttersInSubstring(int startPosition, int endPosition) {
        if (startPosition < 1) throw new IllegalArgumentException("Parameter startPosition < 1");
        if (startPosition > endPosition) throw new IllegalArgumentException("Parameter startPosition > endPosition");
        if (endPosition > currentStr.length() && endPosition > startPosition) throw new MyIndexOutOfBoundsException("Parameter endPosition is out of bounds");

        String tempStr1 = currentStr.substring(0, startPosition - 1);
        String tempStr2 = currentStr.substring(startPosition - 1, endPosition);
        String tempStr3 = currentStr.substring(endPosition, currentStr.length());
        String digitsToEnglishNamesStr = "";

        boolean prevDigitIsContiguous = false; // check previous digit is true or false, initial set with false
        boolean needAppendAsterisk = false; // this flag to indicate a new not contiguous digit, so we can append ending * to the string

        //currentStr = tempStr1 + tempStr2 + tempStr3;
        for (Character currentCharacter : tempStr2.toCharArray()) {
            // Check current digit is true or false using Character.isDigit
            boolean booleanCurrentDigit = Character.isDigit(currentCharacter);

            if (booleanCurrentDigit == true) {
                // Check previous digit is contiguous digit or not, increment total if current digit is true and previous digit is false
                if (prevDigitIsContiguous == false) {
                    digitsToEnglishNamesStr += "*";
                    prevDigitIsContiguous = true; // Set contiguous flag with true
                    needAppendAsterisk = true;
                }

                digitsToEnglishNamesStr += englishNameDigitMap.get(currentCharacter);
            } else {
                // Set contiguous flag with false
                if (needAppendAsterisk == true) {
                    digitsToEnglishNamesStr += "*";
                    needAppendAsterisk = false; // After set ending * then set it with false
                }

                prevDigitIsContiguous = false;
                digitsToEnglishNamesStr += currentCharacter;
            }
        }

        // If the string between the passed parameters passed parameter[startPosition, endPosition]
        // add ending * to the match.
        if (needAppendAsterisk == true) {
            digitsToEnglishNamesStr += "*";
        }

        currentStr = tempStr1 + digitsToEnglishNamesStr + tempStr3;
    }

    public static void main(String[] args) {
        MyCustomString test = new MyCustomString();
        test.setString("123abcdef");
        test.FlipLetttersInSubstring(1, 3);
    }
}



