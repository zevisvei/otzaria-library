# to do:
- המרת טבלאות לhtml
- תבניות באופן אוטומטי
# api
## ויקיטסט
```
https://he.wikisource.org/w/api.php
```
## ויקישיבה
```
https://www.yeshiva.org.il/wiki/api.php
```
## אוצר הספרים היהודי השיתופי
```
https://wiki.jewishbooks.org.il/mediawiki/api.php
```

## קבלת עץ קטגוריות
```
https://he.wikisource.org/w/api.php?action=query&list=allcategories&aclimit=max&format=json&accontinue=
```
## קבלת רשימת הדפים
```
https://he.wikisource.org/w/api.php?action=query&list=allpages&aplimit=max&format=json&accontinue=A2684
```
## קבלת שמות המתחם
```
https://he.wikisource.org/w/api.php?action=query&meta=siteinfo&siprop=namespaces&format=json
```
<a href="https://www.mediawiki.org/wiki/Help:Namespaces">עזרה</a>
| Number | Canonical name   | שם בעברית  |
|--------|------------------|-----------------|
| -2     | Media            | מדיה            |
| -1     | Special          | מיוחד         |
| 0      | (Main)           | (Main)          |
| 1      | Talk             | שיחה            |
| 2      | User             | משתמש            |
| 3      | User talk        | שיחת משתמש       |
| 4      | Project          | שם האתר         |
| 5      | Project talk     | שיחת שם האתר    |
| 6      | File             | קובץ            |
| 7      | File talk        | שיחת קובץ       |
| 8      | MediaWiki        | מדיה ויקי       |
| 9      | MediaWiki talk   | שיחת מדיה ויקי  |
| 10     | Template         | תבנית        |
| 11     | Template talk    | שיחת תבנית   |
| 12     | Help             | עזרה            |
| 13     | Help talk        | שיחת עזרה       |
| 14     | Category         | קטגוריה        |
| 15     | Category talk    | שיחת קטגוריה   |

## קבלת תוכן דף בפורמט html
```
https://he.wikisource.org/w/api.php?action=parse&page=page_title&prop=text&disabletoc=true&disableeditsection=true&format=json

```
## קבלת תוכן הדף בפורמט mediawiki
```
https://he.wikisource.org/w/api.php?action=query&prop=revisions&titles=page_title&rvslots=*&rvprop=content&format=json
```
## קבלת מידע על הדף
```
https://he.wikisource.org/w/api.php?action=query&titles=&prop=categories&format=json
```
## קבלת חברי קטגוריה
```
https://he.wikisource.org/w/api.php?action=query&list=categorymembers&cmtitle=&cmlimit=max&format=json
```
## דפים בשם מתחם מסויים
```
https://he.wikisource.org/w/api.php?action=query&list=allpages&apnamespace=1&aplimit=max&format=json
```