import re
import sys


def cdn_to_raw(url):
    # jsdelivr (包括 testingcf.jsdelivr.net)
    m = re.match(
        r"https://(?:cdn\.|testingcf\.)?jsdelivr\.net/gh/([^/]+)/([^/@]+)@([^/]+)/(.*)",
        url,
    )
    if m:
        owner, repo, branch, path = m.groups()
        # 直接替换-cdn为-raw，兼容所有后缀
        path = path.replace("-cdn", "-raw")
        return f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"
    # fastgit
    m = re.match(r"https://raw\.fastgit\.org/([^/]+)/([^/]+)/([^/]+)/(.*)", url)
    if m:
        owner, repo, branch, path = m.groups()
        path = path.replace("-cdn", "-raw")
        return f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"
    # github.io
    m = re.match(r"https://([^.]+)\.github\.io/([^/]+)/(.*)", url)
    if m:
        user, repo, path = m.groups()
        path = path.replace("-cdn", "-raw")
        return f"https://raw.githubusercontent.com/{user}/{repo}/main/{path}"
    return url


def raw_to_cdn(url, cdn_type="cdn"):
    # raw.githubusercontent.com
    m = re.match(
        r"https://raw\.githubusercontent\.com/([^/]+)/([^/]+)/([^/]+)/(.*)", url
    )
    if m:
        owner, repo, branch, path = m.groups()
        # 直接替换-raw为-cdn，兼容所有后缀
        path = path.replace("-raw", "-cdn")
        # github.io 反向
        if branch == "main":
            return f"https://{owner}.github.io/{repo}/{path}"
        # 使用参数化的 jsdelivr 域名
        return f"https://{cdn_type}.jsdelivr.net/gh/{owner}/{repo}@{branch}/{path}"
    # github.io → jsdelivr
    m = re.match(r"https://([^.]+)\.github\.io/([^/]+)/(.*)", url)
    if m:
        user, repo, path = m.groups()
        path = path.replace("-raw", "-cdn")
        return f"https://{cdn_type}.jsdelivr.net/gh/{user}/{repo}@main/{path}"
    return url


def process_file(filename, cdn_type="cdn"):
    if "-cdn" in filename:
        mode = "cdn2raw"
        outname = filename.replace("-cdn", "-raw")
    elif "-raw" in filename:
        mode = "raw2cdn"
        outname = filename.replace("-raw", "-cdn")
    else:
        print("文件名需包含-cdn或-raw")
        return

    with open(filename, encoding="utf-8") as f:
        content = f.read()

    # 更新编辑时间, 同步自身和目标文件
    # 匹配 # update: YYYY-MM-DD HH:MM:SS
    update_time = re.search(r"# update: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", content)
    if update_time:
        # 替换更新时间为当前时间
        from datetime import datetime

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        content = re.sub(
            update_time.group(0),
            f"# update: {current_time}",
            content,
        )
        # 修改自身更新时间
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)

    # 去除所有 github 代理前缀
    content = re.sub(r"https://ghproxy\.net/", "", content)

    if mode == "cdn2raw":
        # 替换所有CDN为raw
        content = re.sub(
            r"https://(?:cdn\.|testingcf\.)?jsdelivr\.net/gh/[^ \n]+",
            lambda m: cdn_to_raw(m.group()),
            content,
        )
        content = re.sub(
            r"https://raw\.fastgit\.org/[^ \n]+",
            lambda m: cdn_to_raw(m.group()),
            content,
        )
        content = re.sub(
            r"https://[a-zA-Z0-9-]+\.github\.io/[^ \n]+",
            lambda m: cdn_to_raw(m.group()),
            content,
        )
    else:
        # 替换所有raw为CDN
        content = re.sub(
            r"https://raw\.githubusercontent\.com/[^ \n]+",
            lambda m: raw_to_cdn(m.group(), cdn_type),
            content,
        )
        content = re.sub(
            r"https://[a-zA-Z0-9-]+\.github\.io/[^ \n]+",
            lambda m: raw_to_cdn(m.group(), cdn_type),
            content,
        )

    with open(outname, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"已生成: {outname}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python convert2cdn.py 文件名 [cdn类型, 默认cdn, 可选值: cdn, testingcf]")
    else:
        cdn_type = sys.argv[2] if len(sys.argv) > 2 else "cdn"
        process_file(sys.argv[1], cdn_type)
