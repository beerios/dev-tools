def handBrakeExe_win = 'C:\\Program Files (x86)\\Handbrake\\HandBrakeCLI --main-feature -i "%s" -o "%s\\%s.m4v" -f mp4 -Z "AppleTV 3"'// Create the String


def srcDir = new File("M:\\MyMovies\\Movies\\")
def dstDir = new File("F:\\MyMovies\\Movies\\")
def currLetter = null

srcDir.eachDir {
    if (!dstDir.listFiles()*.getName().contains(it.name)) {
		
		//Uncomment to process one letter at a time
		//currLetter = currLetter ?: it.name.getAt(0)
		//if (it.name.getAt(0) != currLetter) {
		//	println 'Completed processing files beginning with ' + currLetter
		//	System.exit(0)
		//}			
		
        println "Begin processing ${it.name}\n..."

		//Create the directory for this movie file
		def dstMovieDir = new File(dstDir.absolutePath.concat("\\").concat(it.name))
		if (!dstMovieDir.mkdir()) {
			println "Failed to create new directory ${dstMovieDir.absolutePath}"
			System.exit(5)
		}
		
		//Copy the dvdid file over
		def srcMovieDir = new File(srcDir.absolutePath.concat("\\").concat(it.name))
		srcMovieDir.eachFile(groovy.io.FileType.FILES) {
			println it.name
			//if (it.name.endsWith('.dvdid.xml')) {
				def copyString = String.format('cmd /c COPY "%s" "%s"', it.canonicalPath, dstMovieDir.canonicalPath )
				println copyString
				copyString.execute()
			//}
		}
		//Useful for testing the folder creation an dvdid copy.  Comment out for full run
		//System.exit(0)

		//Add the src and dst to the exe string
		def exeString = String.format(handBrakeExe_win, srcMovieDir, dstMovieDir, it.name)
        println exeString
        def proc = exeString.execute()                 // Call *execute* on the string
		proc.consumeProcessOutput()
        proc.waitFor()                               // Wait for the command to finish
        if (proc.exitValue() != 0) {
            println("Something when wrong while processing" + it.name)
            // Obtain status and output
            println "return code: ${proc.exitValue()}"
            println "stderr: ${proc.err.text}"
            println "stdout: ${proc.in.text}"
        }
        println "...\nFinished processing ${it.name}"
        //Commented this out to process more than one videos at a time.
		//System.exit(proc.exitValue())
	}
}
println 'Completed processing all files in ' + srcDir
System.exit(0)
