import pytest


class TestCreateBookmark:
    def test_create_success(self, client, auth_headers):
        """创建书签成功"""
        response = client.post(
            "/bookmarks/",
            json={"title": "测试书签", "url": "https://example.com"},
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "测试书签"
        assert data["url"] == "https://example.com"
        assert "id" in data
        assert "created_at" in data

    def test_create_without_auth(self, client):
        """未登录创建书签 → 401"""
        response = client.post(
            "/bookmarks/",
            json={"title": "测试", "url": "https://example.com"}
        )
        assert response.status_code == 401


class TestListBookmarks:
    def test_list_without_auth(self, client):
        """未登录访问列表 → 401"""
        response = client.get("/bookmarks/")
        assert response.status_code == 401

    def test_list_empty(self, client, auth_headers):
        """空列表"""
        response = client.get("/bookmarks/", headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == []

    def test_list_with_items(self, client, auth_headers):
        """有数据"""
        # 先创建一个
        client.post(
            "/bookmarks/",
            json={"title": "Google", "url": "https://google.com"},
            headers=auth_headers
        )
        # 再查
        response = client.get("/bookmarks/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["title"] == "Google"

    def test_list_with_search(self, client, auth_headers):
        """搜索功能"""
        client.post(
            "/bookmarks/",
            json={"title": "Python官网", "url": "https://python.org"},
            headers=auth_headers
        )
        response = client.get("/bookmarks/?q=Python", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert "Python" in data[0]["title"]

    def test_list_pagination(self, client, auth_headers):
        """分页"""
        # 创建 3 条
        for i in range(3):
            client.post(
                "/bookmarks/",
                json={"title": f"书签{i}", "url": f"https://example{i}.com"},
                headers=auth_headers
            )
        response = client.get("/bookmarks/?skip=1&limit=2", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2


class TestGetBookmark:
    def test_get_success(self, client, auth_headers):
        """单条查询成功"""
        # 先创建
        create_resp = client.post(
            "/bookmarks/",
            json={"title": "查询测试", "url": "https://get.com"},
            headers=auth_headers
        )
        bookmark_id = create_resp.json()["id"]

        # 单条查询
        response = client.get(f"/bookmarks/{bookmark_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == bookmark_id
        assert data["title"] == "查询测试"
        assert data["url"] == "https://get.com"
        assert "created_at" in data

    def test_get_not_found(self, client, auth_headers):
        """查询不存在的书签 → 404"""
        response = client.get("/bookmarks/99999", headers=auth_headers)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_without_auth(self, client):
        """未登录查询 → 401"""
        response = client.get("/bookmarks/1")
        assert response.status_code == 401


class TestUpdateBookmark:
    def test_update_success(self, client, auth_headers):
        """更新成功"""
        # 先创建
        create_resp = client.post(
            "/bookmarks/",
            json={"title": "旧标题", "url": "https://old.com"},
            headers=auth_headers
        )
        bookmark_id = create_resp.json()["id"]

        # 更新
        response = client.put(
            f"/bookmarks/{bookmark_id}",
            json={"title": "新标题", "url": "https://new.com"},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "新标题"
        assert data["url"] == "https://new.com"

    def test_update_not_found(self, client, auth_headers):
        """更新不存在的书签 → 404"""
        response = client.put(
            "/bookmarks/99999",
            json={"title": "不存在", "url": "https://nope.com"},
            headers=auth_headers
        )
        assert response.status_code == 404

    def test_partial_update_only_title(self, client, auth_headers):
        """只传 title，url 不传 → url 保持不变"""
        # 先创建
        create_resp = client.post(
            "/bookmarks/",
            json={"title": "原标题", "url": "https://original.com"},
            headers=auth_headers
        )
        bookmark_id = create_resp.json()["id"]

        # 只更新 title，不传 url
        response = client.put(
            f"/bookmarks/{bookmark_id}",
            json={"title": "新标题"},   # url 不传 → None
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "新标题"
        assert data["url"] == "https://original.com"  # url 没变

    def test_partial_update_only_url(self, client, auth_headers):
        """只传 url，title 不传 → title 保持不变"""
        create_resp = client.post(
            "/bookmarks/",
            json={"title": "固定标题", "url": "https://old.com"},
            headers=auth_headers
        )
        bookmark_id = create_resp.json()["id"]

        response = client.put(
            f"/bookmarks/{bookmark_id}",
            json={"url": "https://new-url.com"},   # title 不传 → None
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "固定标题"           # title 没变
        assert data["url"] == "https://new-url.com"

    def test_partial_update_empty_body(self, client, auth_headers):
        """什么都不传 → 两个字段都不变"""
        create_resp = client.post(
            "/bookmarks/",
            json={"title": "不变标题", "url": "https://unchanged.com"},
            headers=auth_headers
        )
        bookmark_id = create_resp.json()["id"]

        response = client.put(
            f"/bookmarks/{bookmark_id}",
            json={},   # 空 body → title=None, url=None
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "不变标题"
        assert data["url"] == "https://unchanged.com"


class TestDeleteBookmark:
    def test_delete_success(self, client, auth_headers):
        """删除成功"""
        # 先创建
        create_resp = client.post(
            "/bookmarks/",
            json={"title": "待删除", "url": "https://delete.com"},
            headers=auth_headers
        )
        bookmark_id = create_resp.json()["id"]

        # 删除
        response = client.delete(f"/bookmarks/{bookmark_id}", headers=auth_headers)
        assert response.status_code == 204

        # 用单条查询接口确认已删除 → 404
        get_resp = client.get(f"/bookmarks/{bookmark_id}", headers=auth_headers)
        assert get_resp.status_code == 404

        # 列表里也不应该有了
        list_resp = client.get("/bookmarks/", headers=auth_headers)
        ids = [b["id"] for b in list_resp.json()]
        assert bookmark_id not in ids

    def test_delete_not_found(self, client, auth_headers):
        """删除不存在的书签 → 404"""
        response = client.delete("/bookmarks/99999", headers=auth_headers)
        assert response.status_code == 404


class TestCrossUserIsolation:
    """Day12 核心测试：跨用户隔离，所有接口返回 404"""

    def test_user_b_cannot_get_user_a_bookmark(self, client, auth_headers, auth_headers2):
        """用户A创建书签，用户B查询 → 404"""
        # 用户A创建
        create_resp = client.post(
            "/bookmarks/",
            json={"title": "A的书签", "url": "https://a.com"},
            headers=auth_headers
        )
        assert create_resp.status_code == 201
        bookmark_id = create_resp.json()["id"]

        # 用户B查询 → 应该 404
        response = client.get(f"/bookmarks/{bookmark_id}", headers=auth_headers2)
        assert response.status_code == 404

    def test_user_b_cannot_list_user_a_bookmarks(self, client, auth_headers, auth_headers2):
        """用户A创建多条书签，用户B列表里看不到"""
        # 用户A创建 2 条
        for i in range(2):
            client.post(
                "/bookmarks/",
                json={"title": f"A的书签{i}", "url": f"https://a{i}.com"},
                headers=auth_headers
            )

        # 用户B列表 → 应该是空的
        response = client.get("/bookmarks/", headers=auth_headers2)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    def test_user_b_cannot_update_user_a_bookmark(self, client, auth_headers, auth_headers2):
        """用户A创建书签，用户B更新 → 404"""
        # 用户A创建
        create_resp = client.post(
            "/bookmarks/",
            json={"title": "A的原始标题", "url": "https://a.com"},
            headers=auth_headers
        )
        bookmark_id = create_resp.json()["id"]

        # 用户B更新 → 应该 404
        response = client.put(
            f"/bookmarks/{bookmark_id}",
            json={"title": "B想改的标题"},
            headers=auth_headers2
        )
        assert response.status_code == 404

    def test_user_b_cannot_delete_user_a_bookmark(self, client, auth_headers, auth_headers2):
        """用户A创建书签，用户B删除 → 404"""
        # 用户A创建
        create_resp = client.post(
            "/bookmarks/",
            json={"title": "A的待删书签", "url": "https://a-delete.com"},
            headers=auth_headers
        )
        bookmark_id = create_resp.json()["id"]

        # 用户B删除 → 应该 404
        response = client.delete(f"/bookmarks/{bookmark_id}", headers=auth_headers2)
        assert response.status_code == 404

        # 用户A仍然能查到（确认没被删）
        get_resp = client.get(f"/bookmarks/{bookmark_id}", headers=auth_headers)
        assert get_resp.status_code == 200
        assert get_resp.json()["title"] == "A的待删书签"

    def test_each_user_only_sees_own_bookmarks(self, client, auth_headers, auth_headers2):
        """两个用户各自创建，列表只返回自己的"""
        # 用户A创建 2 条
        client.post("/bookmarks/", json={"title": "A1", "url": "https://a1.com"}, headers=auth_headers)
        client.post("/bookmarks/", json={"title": "A2", "url": "https://a2.com"}, headers=auth_headers)

        # 用户B创建 1 条
        client.post("/bookmarks/", json={"title": "B1", "url": "https://b1.com"}, headers=auth_headers2)

        # 用户A列表 → 2 条
        resp_a = client.get("/bookmarks/", headers=auth_headers)
        assert resp_a.status_code == 200
        data_a = resp_a.json()
        assert len(data_a) == 2
        titles_a = [b["title"] for b in data_a]
        assert "A1" in titles_a
        assert "A2" in titles_a

        # 用户B列表 → 1 条
        resp_b = client.get("/bookmarks/", headers=auth_headers2)
        assert resp_b.status_code == 200
        data_b = resp_b.json()
        assert len(data_b) == 1
        assert data_b[0]["title"] == "B1"