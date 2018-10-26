package edu.gatech.seclass.encode;

import static org.junit.Assert.*;

import org.junit.After;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.TemporaryFolder;

public class MyMainTest {
	
/*
Place all  of your tests in this class, optionally using MainTest.java as an example.
*/
    private ByteArrayOutputStream outStream;
    private ByteArrayOutputStream errStream;
    private PrintStream outOrig;
    private PrintStream errOrig;
    private Charset charset = StandardCharsets.UTF_8;

    @Rule
    public TemporaryFolder temporaryFolder = new TemporaryFolder();

    @Before
    public void setUp() throws Exception {
        outStream = new ByteArrayOutputStream();
        PrintStream out = new PrintStream(outStream);
        errStream = new ByteArrayOutputStream();
        PrintStream err = new PrintStream(errStream);
        outOrig = System.out;
        errOrig = System.err;
        System.setOut(out);
        System.setErr(err);
    }

    @After
    public void tearDown() throws Exception {
        System.setOut(outOrig);
        System.setErr(errOrig);
    }

    // Some utilities

    private File createTmpFile() throws IOException {
        File tmpfile = temporaryFolder.newFile();
        tmpfile.deleteOnExit();
        return tmpfile;
    }

   private File createEmptyFile() throws Exception {
        File file1 =  createTmpFile();
        FileWriter fileWriter = new FileWriter(file1);

        fileWriter.close();
        return file1;
    }

    private File createInputFile1() throws Exception {
        File file1 =  createTmpFile();
        FileWriter fileWriter = new FileWriter(file1);

        fileWriter.write("abcdefgh");

        fileWriter.close();
        return file1;
    }

    private File createInputFile2() throws Exception {
        File file2 =  createTmpFile();
        FileWriter fileWriter = new FileWriter(file2);

        fileWriter.write("Howdy Billy,\n"+
                "I am going to take cs6300 and cs6400 next semester.\n");
       fileWriter.close();
        return file2;
    }



    private String getFileContent(String filename) {
        String content = null;
        try {
            content = new String(Files.readAllBytes(Paths.get(filename)), charset);
        } catch (IOException e) {
            e.printStackTrace();
        }
        return content;
    }

        // test cases

// Purpose: The purpose of this test case is to test the error scenario of given file in argument not present
// Frame #: <test case number 1 in the catpart.txt.tsl of Part I>
    @Test
    public void encodeTest1() throws Exception {

        String args[] = {"errtest1.txt"};
        Main.main(args);
        assertEquals("File Not Present ", errStream.toString().trim());
    }

// Purpose: The purpose of this test case is to test the error scenario of size of given file in argument is zero
// Frame #: <test case number 2 in the catpart.txt.tsl of Part I>
    @Test
    public void encodeTest2() throws Exception {

        File inputFile1 = createEmptyFile();

        String args[] = {inputFile1.getPath()};
        Main.main(args);
        assertEquals("Given file is empty ", errStream.toString().trim());
    }

// Purpose: The purpose of this test case is to test the scenario of no options provided in the command line argument
// Frame #: <test case number 3 in the catpart.txt.tsl of Part I>
    @Test
    public void encodeTest3() throws Exception {
        File inputFile1 = createInputFile1();

        String args[] = {inputFile1.getPath()};
        Main.main(args);

        String expected1 = "ijklmnop";

        String actual1 = getFileContent(inputFile1.getPath());

        assertEquals("The files differ!", expected1, actual1);
    }

// Purpose: The purpose of this test case is to test the error scenario of no value provided along with argument c in the command line
// Frame #: <test case number 4 in the catpart.txt.tsl of Part I>
    @Test
    public void encodeTest4() throws Exception {
        File inputFile1 = createInputFile1();

        String args[] = {"-c",inputFile1.getPath()};

        Main.main(args);
        assertEquals("Usage: Encode  [-c int] [-d string] [-r] <filename>", errStream.toString().trim());
    }


// Purpose: The purpose of this test case is to test the error scenario of non-integer value provided along with argument c in the command line
// Frame #: <test case number 5 in the catpart.txt.tsl of Part I>
    @Test
    public void encodeTest5() throws Exception {
        File inputFile1 = createInputFile1();

        String args[] = {"-c","abn&^89",inputFile1.getPath()};

        Main.main(args);
        assertEquals("Usage: Encode  [-c int] [-d string] [-r] <filename>", errStream.toString().trim());
    }

// Purpose: The purpose of this test case is to test the error scenario of no value provided along with argument d in the command line
// Frame #: <test case number 7 in the catpart.txt.tsl of Part I>
    @Test
    public void encodeTest6() throws Exception {
        File inputFile1 = createInputFile1();

        String args[] = {"-d",inputFile1.getPath()};

        Main.main(args);
        assertEquals("Usage: Encode  [-c int] [-d string] [-r] <filename>", errStream.toString().trim());
    }

// Purpose: The purpose of this test case is to test the error scenario of a value provided along with argument r in the command line
// Frame #: <test case number 8 in the catpart.txt.tsl of Part I>
    @Test
    public void encodeTest7() throws Exception {
        File inputFile1 = createInputFile1();

        String args[] = {"-r","adh78^",inputFile1.getPath()};

        Main.main(args);
        assertEquals("Usage: Encode  [-c int] [-d string] [-r] <filename>", errStream.toString().trim());
    }

// Purpose: The purpose of this test case is to test the  scenario of 3 value provided along with argument c,alpha numeric characters provided as a value for argument d and r present in the options
// Frame #: <test case number 29 in the catpart.txt.tsl of Part I>
    @Test
    public void encodeTest8() throws Exception {
        File inputFile1 = createInputFile2();

        String args[] = {"-c","3","-d","ao0u","-r",inputFile1.getPath()};

        Main.main(args);
        String expected3 = "bgaK ,boolE\n"+
                 "L p jqlj w hnw 36vf gq 46vf wahq .uhwvhphv\n";

        String actual3 = getFileContent(inputFile1.getPath());

        assertEquals("The files differ!", expected3, actual3);
    }

// Purpose: The purpose of this test case is to test the  scenario of  0 value provided along with argument c,alpha numeric characters provided as a value for argument d and -r present in the options
// Frame #: <test case number 9 in the catpart.txt.tsl of Part I>
    @Test
    public void encodeTest9() throws Exception {
        File inputFile1 = createInputFile2();

        String args[] = {"-c","0","-d","ao0u","-r",inputFile1.getPath()};

        Main.main(args);
        String expected3 = "ydwH ,ylliB\n" +
                 "I m gnig t ekt 36sc dn 46sc txen .retsemes\n";

        String actual3 = getFileContent(inputFile1.getPath());

        assertEquals("The files differ!", expected3, actual3);
    }

// Purpose: The purpose of this test case is to test the  scenario of >26 value provided along with argument c,alpha numeric characters provided as a value for argument d and -r not present
// Frame #: <test case number 20 in the catpart.txt.tsl of Part I>
    @Test
    public void encodeTest10() throws Exception {
        File inputFile1 = createInputFile2();

        String args[] = {"-c","29","-d","ao0u",inputFile1.getPath()};

        Main.main(args);


        String expected3 = "Kagb Eloob,\n"+
                 "L p jlqj w wnh fv63 qg fv64 qhaw yhphvwhu.\n";

        String actual3 = getFileContent(inputFile1.getPath());

        assertEquals("The files differ!", expected3, actual3);
    }

// Purpose: The purpose of this test case is to test the  scenario of <26 value provided along with argument c,all characters including space provided as a value for argument d and -r  present
// Frame #: <test case number 35 in the catpart.txt.tsl of Part I>
    @Test
    public void encodeTest11() throws Exception {
        File inputFile1 = createInputFile2();

        String args[] = {"-c","3","-d","ao,. 0u","-r",inputFile1.getPath()};

        Main.main(args);


        String expected3 = "boolEbgaK\n"+
                "uhwyhphywahq46vfgq36vfhnwwjqljpL\n";

        String actual3 = getFileContent(inputFile1.getPath());

        assertEquals("The files differ!", expected3, actual3);
    }

// Purpose: The purpose of this test case is to test the  scenario of <0 value provided along with argument c,alpha numeric characters provided as a value for argument d and -r not present
// Frame #: <test case number 40 in the catpart.txt.tsl of Part I>
    @Test
    public void encodeTest12() throws Exception {
        File inputFile1 = createInputFile2();

        String args[] = {"-c","-3","-d","ao0u",inputFile1.getPath()};

        Main.main(args);


        String expected3 = "Etav Yfiiv,\n"+
                "F j dfkd q qhb zp63 ka zp64 kbuq pbjbpqbo.\n";

        String actual3 = getFileContent(inputFile1.getPath());

        assertEquals("The files differ!", expected3, actual3);
    }


// Purpose: The purpose of this test case is to test the  scenario of <0 value provided along with argument c,argument d and r not present
// Frame #: <test case number 48 in the catpart.txt.tsl of Part I>
    @Test
    public void encodeTest13() throws Exception {
        File inputFile1 = createInputFile1();

        String args[] = {"-c","-3",inputFile1.getPath()};

        Main.main(args);


        String expected3 = "xyzabcde";

        String actual3 = getFileContent(inputFile1.getPath());

        assertEquals("The files differ!", expected3, actual3);
    }

// Purpose: The purpose of this test case is to test the  scenario of only white space  provided along with argument d,argument c and r not present
// Frame #: <test case number 54 in the catpart.txt.tsl of Part I>
    @Test
    public void encodeTest14() throws Exception {
        File inputFile1 = createInputFile2();

        String args[] = {"-d","  ",inputFile1.getPath()};

        Main.main(args);


        String expected3 = "HowdyBilly,\n"+
                "Iamgoingtotakecs6300andcs6400nextsemester.\n";

        String actual3 = getFileContent(inputFile1.getPath());

        assertEquals("The files differ!", expected3, actual3);
    }

// Purpose: The purpose of this test case is to test the  scenario of only  with argument r,argument c and d not present
// Frame #: <test case number 57 in the catpart.txt.tsl of Part I>
    @Test
    public void encodeTest15() throws Exception {
        File inputFile1 = createInputFile1();

        String args[] = {"-r",inputFile1.getPath()};

        Main.main(args);


        String expected3 = "hgfedcba";

        String actual3 = getFileContent(inputFile1.getPath());

        assertEquals("The files differ!", expected3, actual3);
    }
}
