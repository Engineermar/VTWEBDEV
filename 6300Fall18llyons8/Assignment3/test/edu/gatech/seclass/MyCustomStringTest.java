package edu.gatech.seclass;

        import org.junit.After;
        import org.junit.Before;
        import org.junit.Test;

        import static org.junit.Assert.assertEquals;

public class MyCustomStringTest {

    private MyCustomStringInterface mycustomstring;

    // Set up actual concrete class MyCustomStringImplementation before testing
    @Before
    public void setUp() {
        mycustomstring = new MyCustomStringImplementation();
    }

    // Cleanup after testing
    @After
    public void tearDown() {
        mycustomstring = null;
    }

    // Test parameter string is null, return 0
    @Test
    public void testCountDuplicates1() {
        mycustomstring.setString(null);
        assertEquals(0, mycustomstring.countDuplicates());
    }

    // Test parameter string is empty "", return 0
    @Test
    public void testCountDuplicates2() {
        mycustomstring.setString("");
        assertEquals(0, mycustomstring.countDuplicates());
    }

    // Test parameter string is unset without digits "abc", return 0
    @Test
    public void testCountDuplicates3() {
        mycustomstring.setString("abc");
        assertEquals(0, mycustomstring.countDuplicates());
    }

    // Test parameter string is "1", return 1
    @Test
    public void testCountDuplicates4() {
        mycustomstring.setString("1");
        assertEquals(1, mycustomstring.countDuplicates());
    }

    // Test parameter string is "11", return 1
    @Test
    public void testCountDuplicates5() {
        mycustomstring.setString("11");
        assertEquals(1, mycustomstring.countDuplicates());
    }

    // Test parameter string is "11ab2", return 2
    @Test
    public void testCountDuplicates6() {
        mycustomstring.setString("11ab2");
        assertEquals(2, mycustomstring.countDuplicates());
    }

    // Test parameter string is "11ab2222", return 2
    @Test
    public void testCountDuplicates7() {
        mycustomstring.setString("11ab2222");
        assertEquals(2, mycustomstring.countDuplicates());
    }

    // Test parameter string is "cc11ab2dddd3333333333333", return 3
    @Test
    public void testCountDuplicates8() {
        mycustomstring.setString("cc11ab2dddd3333333333333");
        assertEquals(3, mycustomstring.countDuplicates());
    }

    // Test parameter string is "I'd b3tt3r put s0me d161ts in this 5tr1n6, right?", return 7
    @Test
    public void testCountDuplicates9() {
        mycustomstring.setString("I'd b3tt3r put s0me d161ts in this 5tr1n6, right?");
        assertEquals(7, mycustomstring.countDuplicates());
    }

    // Test parameter string is null, expected NullPointerException case
    @Test(expected = NullPointerException.class)
    public void testaddDigits1() {
        mycustomstring.setString(null);
        mycustomstring.addDigits(1, true);
    }

    // Test parameter string is "", n is 1 expected MyIndexOutOfBoundsException case
    @Test(expected = MyIndexOutOfBoundsException.class)
    public void testaddDigits2() {
        mycustomstring.setString("");
        mycustomstring.addDigits(1, true);
    }

    // Test parameter string is "abcd", n is 5 expected MyIndexOutOfBoundsException case
    @Test(expected = MyIndexOutOfBoundsException.class)
    public void testaddDigits3() {
        mycustomstring.setString("abcd");
        mycustomstring.addDigits(5, true);
    }

    // Test parameter string is "abcd", n is 0 expected IllegalArgumentException case
    @Test(expected = IllegalArgumentException.class)
    public void testaddDigits4() {
        mycustomstring.setString("abcd");
        mycustomstring.addDigits(0, true);
    }

    // Test parameter string is "abcd", n is -1 expected IllegalArgumentException case
    @Test(expected = IllegalArgumentException.class)
    public void testaddDigits5() {
        mycustomstring.setString("abcd");
        mycustomstring.addDigits(-1, true);
    }

    // Test parameter string is "abcd", n is 1, return "abcd"
    @Test
    public void testaddDigits6() {
        mycustomstring.setString("abcd");
        assertEquals("abcd", mycustomstring.addDigits(1, true));
    }

    // Test parameter string is "abcd", n is 2, return "bd"
    @Test
    public void testaddDigits7() {
        mycustomstring.setString("abcd");
        assertEquals("bd", mycustomstring.addDigits(2, true));
    }

    // Test parameter string is "abcd", n is 3, return "c"
    @Test
    public void testaddDigits8() {
        mycustomstring.setString("abcd");
        assertEquals("c", mycustomstring.addDigits(3, true));
    }

    // Test parameter string is "abcd", n is 4, return "d"
    @Test
    public void testaddDigits9() {
        mycustomstring.setString("abcd");
        assertEquals("d", mycustomstring.addDigits(4, true));
    }

    // Test parameter string is "abcdefghijklmn", n is 3, return "cfil"
    @Test
    public void testaddDigits10() {
        mycustomstring.setString("abcdefghijklmn");
        assertEquals("cfil", mycustomstring.addDigits(3, true));
    }

    // Test parameter string is "abcdefghijklmn", n is 1, return ""
    @Test
    public void testaddDigits11() {
        mycustomstring.setString("abcdefghijklmn");
        assertEquals("", mycustomstring.addDigits(1, false));
    }

    // Test parameter string is "abcdefghijklmn", n is 2, return "acegikm"
    @Test
    public void testaddDigits12() {
        mycustomstring.setString("abcdefghijklmn");
        assertEquals("acegikm", mycustomstring.addDigits(2, false));
    }

    // Test parameter string is "abcdefghijklmn", n is 3, return "abdeghjkmn"
    @Test
    public void testaddDigits13() {
        mycustomstring.setString("abcdefghijklmn");
        assertEquals("abdeghjkmn", mycustomstring.addDigits(3, false));
    }

    // Test parameter string is "abcdefghijklmn", n is 4, return "abcefgijkmn"
    @Test
    public void testaddDigits14() {
        mycustomstring.setString("abcdefghijklmn");
        assertEquals("abcefgijkmn", mycustomstring.addDigits(4, false));
    }

    // Test parameter string is "abcdefghijklmn", n is 13, return "abcdefghijkln"
    @Test
    public void testaddDigits15() {
        mycustomstring.setString("abcdefghijklmn");
        assertEquals("abcdefghijkln", mycustomstring.addDigits(13, false));
    }

    // Test parameter string is "abcdefghijklmn", n is 14, return "abcdefghijklm"
    @Test
    public void testaddDigits16() {
        mycustomstring.setString("abcdefghijklmn");
        assertEquals("abcdefghijklm", mycustomstring.addDigits(14, false));
    }

    // Test parameter startPosition is 0(If "startPosition" < 1 case), expected IllegalArgumentException case
    @Test(expected = IllegalArgumentException.class)
    public void testFlipLetttersInSubstring1() {
        mycustomstring.setString("abcd");
        int startPosition = 0;
        int endPosition = 3;
        mycustomstring.FlipLetttersInSubstring(startPosition, endPosition);
    }

    // Test parameter startPosition is -1(If "startPosition" < 1 case), expected IllegalArgumentException case
    @Test(expected = IllegalArgumentException.class)
    public void testFlipLetttersInSubstring2() {
        mycustomstring.setString("abcd");
        int startPosition = -1;
        int endPosition = 3;
        mycustomstring.FlipLetttersInSubstring(startPosition, endPosition);
    }

    // Test parameter startPosition is -1("startPosition" > "endPosition" case), expected IllegalArgumentException case
    @Test(expected = IllegalArgumentException.class)
    public void testFlipLetttersInSubstring3() {
        mycustomstring.setString("abcd");
        int startPosition = 3;
        int endPosition = 2;
        mycustomstring.FlipLetttersInSubstring(startPosition, endPosition);
    }

    // Test parameter startPosition is -1("startPosition" > "endPosition" case), expected MyIndexOutOfBoundsException case
    @Test(expected = MyIndexOutOfBoundsException.class)
    public void testFlipLetttersInSubstring4() {
        mycustomstring.setString("abcd");
        int startPosition = 3;
        int endPosition = 5;
        mycustomstring.FlipLetttersInSubstring(startPosition, endPosition);
    }

    // Test current string="1abcdef" no digits in the string, expected "*one*abcdef"
    @Test
    public void testFlipLetttersInSubstring5() {
        mycustomstring.setString("1abcdef");
        mycustomstring.FlipLetttersInSubstring(1, 2);
        assertEquals("*one*abcdef", mycustomstring.getString());
    }

    // Test current string="123abcdef",startPosition=1, endPosition=4, expected "*onetwothree*abcdef"
    @Test
    public void testFlipLetttersInSubstring6() {
        mycustomstring.setString("123abcdef");
        mycustomstring.FlipLetttersInSubstring(1, 4);
        assertEquals("*onetwothree*abcdef", mycustomstring.getString());
    }

    // Test current string="12ab9ghi",startPosition=5, endPosition=6, expected "12ab*nine*ghi"
    @Test
    public void testFlipLetttersInSubstring7() {
        mycustomstring.setString("12ab9ghi");
        mycustomstring.FlipLetttersInSubstring(5, 6);
        assertEquals("12ab*nine*ghi", mycustomstring.getString());
    }

    // Test current string="12ab90ghi",startPosition=5, endPosition=6, expected "12ab*ninezero*ghi"
    @Test
    public void testFlipLetttersInSubstring8() {
        mycustomstring.setString("12ab90ghi");
        mycustomstring.FlipLetttersInSubstring(5, 6);
        assertEquals("12ab*ninezero*ghi", mycustomstring.getString());
    }

    // Test current string="1a90c3ghi",startPosition=2, endPosition=7, expected "1a*ninezero*c*three*ghi"
    @Test
    public void testFlipLetttersInSubstring9() {
        mycustomstring.setString("1a90c3ghi");
        mycustomstring.FlipLetttersInSubstring(2, 7);
        assertEquals("1a*ninezero*c*three*ghi", mycustomstring.getString());
    }

    //Test current string="abcdef" no digits in the string, expected the same string, no changes
    @Test
    public void testFlipLetttersInSubstring10() {
        mycustomstring.setString("I'd b3tt3r put s0me d161ts in this 5tr1n6, right?");
        mycustomstring.FlipLetttersInSubstring(17, 23);
        assertEquals("I'd b3tt3r put s*zero*me d*onesix*1ts in this 5tr1n6, right?", mycustomstring.getString());
    }
}


