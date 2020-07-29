# extract-photos
A handy python based GUI script for wedding photographers to speed up the post production workflow.

# who is it created for?
   Event photographers (especially for wedding photographers) who deals with 1000s of images.
 
# How this tool works?
### A sample scenario
   Consider you have 1000s of RAW Photos from an event photoshoot. And you want to give all those photos for your client for shortlisting. E.g. My Wedding clients would select 200 photos out of 2500 pics for printing a wedding album.
   
   The problem is, it is hard to transfer 2500 RAW photos of size more than 20Gigs to the client, and mostly impossible for the client to view the RAW images from their mobile/desktop.
   
   So, photographers generally compress and convert the RAW photos (Via Lightroom or Darktable) to simple JPEGs of each size 100-200Kb and send the photos via cloud for them to shortlist. 
   
### How does this tool help photographers. 
    
    Folder -A) Now you have a Original RAW pics folder called "Main Source" that contain 1000s of RAW images in Full Quality.
    
    Folder -B) And the client has shortlisted 100 photos from the low-quality JPEGs that you sent them. Now you have all those low-quality JPEGs saved in folder called "Selected Photos"
    
    Folder -C) You want to extract those 100 short listed photos to a separate folder and edit/retouch the photos before you print them. 
    
 
 Open this script, Just paste the folder path of A), B) and C) this script will automatically compare and copy the High Res RAW images to the folder C). 
 
 # Road Map
     - Automatically upload the low-quality JPEGs to a cloud service and email the client.
     
     - Integrate this process of extracting selected photos into Lightroom using EXIFTOOL and XMP side car files - so that there is no need to have redundant images stored in Folder -C)
    

    
