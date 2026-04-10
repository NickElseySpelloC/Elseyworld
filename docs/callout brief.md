Please create the shortcode file layouts/shortcodes/callout.html

This will allow me to insert an inline "call out" box within the body of a markdown document. The box should be styled as follows:

- padding:  20px
- border: 2px solid
- border-radius: 8px
- border colour: light grey if system is "light mode", dark grey otherwise.
- background colour: very light grey if system is "light mode". If system is "dark mode" then just a bit lighter than the theme background colour. Simply put, I want the box's background colour to be subtly darker or lighter than the theme backgound colour, for system light and dark mode, respectively.
- Box takes up the full available width of the content.

Now create a second shortcode: layouts/shortcodes/callout-float.html

This has the same properties as callout.html, except that this floats left or right:

- Float style is a parameter passed to callout-float.html.
- By default, the box takes up 65% of the available content width, but this can be changed by a parameter.

The example markdown content below has two call out boxes. The first inline, the second floating left that consumes 70% of the content width. In the second example, the subsequent paragraph will flow around to the right of the box.

```markdown
### Setting the scene

The NSW jury trial system, which is based on Section 80 of the Constitution (which, in turn, is based on the US Constitution) states that the “trial on indictment of any offence against any law of the Commonwealth shall be by jury” and that any person charged with a serious offence is entitled to have his or her innocence or guilt determined by their peers.

{{< callout >}}
The 12 ordinary citizens who comprise a normal jury are deemed to be representative of the community. Because the jury process is secret, jurors are presumed to consider the case based on community values rather than external pressures, eliminating problems or perceptions that a judge or magistrate, for example, could be biased, side with authority, or are removed from the day-to- day life of ordinary people.
{{< /callout >}}

Research has found that judges who regularly hear criminal prosecutions without juries become “case-hardened” and are biased towards prosecution (Graham Fricke QC, “Trial by Jury”, Parliamentary Research Paper 1996-97).

### Jury selection

Juror anonymity is a feature of NSW criminal trial process, in stark contrast to other jurisdictions, such as the US, where attorneys receive information on prospective jurors and are allowed to question them about their values and beliefs. In the US, jury selection in high-profile cases often involves jury consultants who undertake an array of methods to try to uncover details about the prospective jurors.

In NSW, however, jurors are identified only by a number, so challenges are based solely on what the person looks like.

{{< callout-float side="left" width="70%" >}}
Following concerns that juries were mainly comprised of students, housewives and retirees, in recent years efforts have been made to try to ensure that a jury is more reflective of the community, including making it more difficult for people to avoid serving.
{{< /callout-float >}}

“There seems to be more diversity on juries now, due to changes in who can serve and possibly that grounds for exemption are more difficult to get,” says Professor Nicholas Cowdery, AM QC, who served as the Director of Public Prosecutions for NSW from 1994-2011.

Recent statistics from the NSW Sheriff back his observations. From February 2016 to February 2017, 81 per cent of jurors were employed, with ages fairly evenly spread across groups:
```