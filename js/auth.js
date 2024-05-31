// 检查用户是否已登录
function isLoggedIn() {
    item = JSON.parse(localStorage.getItem('item'));
    return item.isLoggedIn === 'true';
}

// 检查用户是否有访问该页面的权限
function hasPermission(page) {
    item = JSON.parse(localStorage.getItem('item'));
    permissions = item.permissions;
    console.log(page)
    return permissions && permissions.includes(page);
}

function checkExpire() {
    const currentTime = new Date().getTime();
    item = JSON.parse(localStorage.getItem('item'));
    if ( !item ) {
        return false;
    }
    const expireTime = item.expiry;

    if (expireTime && currentTime > expireTime) {
        localStorage.removeItem('item');
        return false;
    }

    return true;
}

// 验证访问权限
function checkAccess() {
    const currentPath = window.location.pathname;

    if (!checkExpire()) {
        alert('Your session has expired. Please log in again.');
        window.location.href = '/index.html';
        return;
    }

    if (!isLoggedIn()) {
        alert('You are not logged in!');
        window.location.href = '/index.html';
        return;
    }

    if (!hasPermission(currentPath)) {
        alert('You do not have permission to access this page!');
        window.location.href = '/unauthorized.html'; // 未授权页面
    }
}

// 执行权限检查
checkAccess();