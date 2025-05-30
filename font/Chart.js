// در یک پروژه واقعی، این تابع به بک‌اند شما متصل می‌شود
async function fetchAnalysisData(productName, productImage) {
    let apiUrl = 'https://your-backend-api.com/analyze'; // آدرس API بک‌اند شما
    let options = {};

    if (productImage) {
        // اگر تصویر انتخاب شده باشد، درخواست POST با FormData
        const formData = new FormData();
        formData.append('image', productImage);
        options = {
            method: 'POST',
            body: formData // FormData به صورت خودکار Content-Type را تنظیم می‌کند
        };
        // اگر بک‌اند شما نیاز به نام محصول در کنار تصویر دارد، آن را هم اضافه کنید
        if (productName) {
            formData.append('name', productName);
        }
    } else if (productName) {
        // اگر فقط نام محصول وارد شده باشد، درخواست GET
        apiUrl += `?query=${encodeURIComponent(productName)}`;
        options = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        };
    } else {
        return null; // هیچ ورودی معتبری وجود ندارد
    }

    try {
        const response = await fetch(apiUrl, options);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching analysis data:', error);
        alert('خطا در دریافت اطلاعات تحلیل. لطفاً دوباره تلاش کنید.');
        return null;
    }
}

// به‌روزرسانی analyzeButton.addEventListener
analyzeButton.addEventListener('click', async () => {
    const productName = productNameInput.value.trim();
    const productImage = productImageInput.files[0];

    if (!productName && !productImage) {
        alert("لطفاً نام محصول یا موضوع را وارد کنید یا یک تصویر انتخاب نمایید.");
        return;
    }

    // نمایش یک لودینگ (اختیاری)
    analyzeButton.textContent = 'در حال تحلیل...';
    analyzeButton.disabled = true;

    const dataToRender = await fetchAnalysisData(productName, productImage);

    // پنهان کردن لودینگ
    analyzeButton.textContent = 'تحلیل کن';
    analyzeButton.disabled = false;

    if (dataToRender) {
        let title = productName || "تحلیل محصول/موضوع"; // اگر نام محصول نبود، عنوان عمومی
        if (productImage && !productName) {
            title = "تحلیل تصویر محصول";
        } else if (productImage && productName) {
            title = `تحلیل: ${productName} (از تصویر)`;
        }
        renderAnalysis(dataToRender, title);
    }
});