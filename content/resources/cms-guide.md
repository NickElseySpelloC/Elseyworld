---
title: "CMS Guide"
description: "Guide to posting a blog on ElseyWorld"
---
Using Decap CMS at elseyworks.com.

## Step 1: Log In

1. Go to **[elseyworks.com/admin](https://elseyworks.com/admin>)**
2. Click **"Login with GitHub"**
3. If prompted, authorise the app on GitHub
4. You'll land on the Decap CMS dashboard

## Step 2: Create a New Post

1. In the left sidebar, click **"Travel Blog"** (or **"Lynn's Articles"** for Lynn's content)
2. Click the **"New Travel Blog"** button (top right)
3. A blank post editor will open

## Step 3: Fill In the Post Details

At the top of the editor you'll see several fields:

| Field | What to enter |
| --- | --- |
| **Title** | The title of your post, e.g. "A Weekend in Verona" |
| **Date** | The date of the post — click to get a date picker |
| **Author** | Your name (pre-filled) |
| **Thumbnail Image** | Select a thumbnail image to be used on the blog listing page. This can be one of the images used in the body. |
| **Draft** | Leave ON (true) while writing, turn OFF when ready to publish |
| **Categories** | Type a category and press Enter, e.g. "South Pacific 1997" |

## Step 4: Write Your Content

The large area below the fields is the **body editor**. It works like a basic word processor:

- **Bold** — highlight text and click B
- **Italic** — highlight text and click I
- **Headings** — click the H1/H2 dropdown
- **Links** — highlight text and click the chain icon, paste the URL
- **Images** — click the image icon, then "Choose an image" to upload from your computer (see below)

> 💡 **Tip:** You can toggle between the rich text editor and raw Markdown using the button in the top-right of the body editor. Use rich text for normal editing.

## Step 5: Images

Use these special file names when uploading images:

- **thumbnail.jpg** The image will appear as a thumbnail on the listing page.
- **cover.jpg**: The will appear as the cover (hero) image at the top of the content page.
- **feature.jpg**: The image will be used for both the thumbnail and cover image.

See [Feature cover and thumbnail images](https://jpanther.github.io/congo/docs/getting-started/#feature-cover-and-thumbnail-images) for more information.

## Step 6: Save a Draft

At any point while writing, click **"Save"** (top right). This saves your work without publishing it. The post will be marked as a draft and won't appear on the live website yet.

You can come back and continue editing later — just click the post title in the Travel Blog list.

## Step 7: Preview Your Post

Click the **"Preview"** toggle (eye icon, top right of the editor) to see roughly how your post will look. Note this is an approximation — the live site may look slightly different.

## Step 8: Publish

When you're happy with the post:

1. Find the **"Draft"** toggle in the post fields at the top
2. Switch it to **OFF** (false)
3. Click **"Publish"** (or **"Save"**)

This commits the post to GitHub. Within about **60 seconds**, GitHub Actions will automatically rebuild the site and your post will appear live at **<https://elseyworks.com>**.

## Editing an Existing Post

1. Go to **<https://elseyworks.com/admin>**
2. Click **"Travel Blog"** or **"Lynn's Articles"** in the sidebar
3. Find your post in the list and click it
4. Make your changes
5. Click **"Save"** — the site rebuilds automatically

## Things to Remember

- ✅ **Draft = ON** means the post is hidden from the public
- ✅ **Draft = OFF** means the post is live
- ✅ Images you upload go into the site's image library automatically
- ⚠️ **Floated images** (text wrapping around a photo) need to be added by Nick — just let him know where you want them
- ⚠️ After publishing, allow **up to 60 seconds** for the site to rebuild before the post appears live

---

## Something Went Wrong?

| Problem | Solution |
| --- | --- |
| Can't log in | Make sure you're using your GitHub account |
| Post not appearing after publish | Wait 60 seconds and hard-refresh (Cmd+Shift+R) |
| Image won't upload | Check file is JPG or PNG and under 10MB |
| Accidentally published | Edit the post, set Draft back to ON, and Save |

---

Last updated: April 2026
